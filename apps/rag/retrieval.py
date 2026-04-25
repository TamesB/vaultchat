from __future__ import annotations

from dataclasses import dataclass

from django.conf import settings

from apps.rag.models import DocumentChunk
from apps.rag.openai_client import get_openai_client
from pgvector.django import CosineDistance


@dataclass(frozen=True)
class RetrievedChunk:
    content: str
    source_filename: str
    document_id: str


def embed_query(text: str) -> list[float]:
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set")
    client = get_openai_client()
    resp = client.embeddings.create(model=settings.OPENAI_EMBEDDING_MODEL, input=[text])
    return resp.data[0].embedding


def retrieve_chunks(organization_id, query: str, k: int = 6) -> list[RetrievedChunk]:
    qvec = embed_query(query)

    qs = (
        DocumentChunk.objects.filter(organization_id=organization_id)
        .annotate(distance=CosineDistance("embedding", qvec))
        .order_by("distance")
        .select_related("document")
    )[:k]

    out: list[RetrievedChunk] = []
    for c in qs:
        out.append(
            RetrievedChunk(
                content=c.content,
                source_filename=c.metadata.get("source_filename") or c.document.filename,
                document_id=str(c.document_id),
            )
        )
    return out

