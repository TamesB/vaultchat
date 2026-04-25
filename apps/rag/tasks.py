from __future__ import annotations

from celery import shared_task
from django.conf import settings
from django.db import transaction
from pypdf import PdfReader

from apps.documents.models import Document
from apps.rag.ingest import chunk_text
from apps.rag.models import DocumentChunk
from apps.rag.openai_client import get_openai_client


def _extract_pdf_text(path: str) -> str:
    reader = PdfReader(path)
    parts: list[str] = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            parts.append("")
    return "\n".join(parts).strip()


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def ingest_document(self, document_id: str) -> None:
    doc = Document.objects.select_related("organization").get(id=document_id)
    doc.status = Document.Status.PROCESSING
    doc.save(update_fields=["status"])

    try:
        text = _extract_pdf_text(doc.file.path)
        chunks = chunk_text(text)

        client = get_openai_client()
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not set")

        # Embed in batches
        batch_size = 64
        vectors: list[list[float]] = []
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start : start + batch_size]
            resp = client.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL,
                input=[c.content for c in batch],
            )
            vectors.extend([d.embedding for d in resp.data])

        with transaction.atomic():
            DocumentChunk.objects.filter(document_id=doc.id).delete()
            DocumentChunk.objects.bulk_create(
                [
                    DocumentChunk(
                        organization_id=doc.organization_id,
                        document_id=doc.id,
                        chunk_index=chunk.index,
                        content=chunk.content,
                        embedding=vectors[i],
                        metadata={"source_filename": doc.filename},
                    )
                    for i, chunk in enumerate(chunks)
                ],
                batch_size=500,
            )

        doc.status = Document.Status.READY
        doc.save(update_fields=["status"])
    except Exception:
        doc.status = Document.Status.FAILED
        doc.save(update_fields=["status"])
        raise

