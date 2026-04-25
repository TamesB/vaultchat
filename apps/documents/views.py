from __future__ import annotations

import boto3
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings
from django.views.decorators.http import require_http_methods

from .forms import DocumentUploadForm
from .models import Document
from apps.rag.tasks import ingest_document
from apps.audit.models import AuditEvent
from apps.billing.decorators import paid_required


@login_required
@paid_required
@require_http_methods(["GET", "POST"])
def documents_index(request: HttpRequest) -> HttpResponse:
    if request.user.organization_id is None:
        return render(request, "documents/no_org.html", status=400)

    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.cleaned_data["file"]
            doc = Document.objects.create(
                organization_id=request.user.organization_id,
                uploaded_by_id=request.user.id,
                file=f,
                filename=getattr(f, "name", "document.pdf"),
                status=Document.Status.UPLOADED,
            )
            AuditEvent.objects.create(
                organization_id=request.user.organization_id,
                user_id=request.user.id,
                event_type="document.uploaded",
                payload={"document_id": str(doc.id), "filename": doc.filename},
            )
            ingest_document.delay(str(doc.id))
            return redirect("documents:detail", document_id=str(doc.id))
    else:
        form = DocumentUploadForm()

    docs = Document.objects.filter(organization_id=request.user.organization_id).order_by("-created_at")[:50]
    return render(request, "documents/index.html", {"form": form, "documents": docs})


@login_required
@paid_required
def document_detail(request: HttpRequest, document_id: str) -> HttpResponse:
    if request.user.organization_id is None:
        return render(request, "documents/no_org.html", status=400)

    doc = get_object_or_404(Document, id=document_id, organization_id=request.user.organization_id)
    return render(request, "documents/detail.html", {"document": doc})


@login_required
@paid_required
def document_download(request: HttpRequest, document_id: str) -> HttpResponse:
    if request.user.organization_id is None:
        return render(request, "documents/no_org.html", status=400)

    doc = get_object_or_404(Document, id=document_id, organization_id=request.user.organization_id)

    key = doc.file.name
    s3 = boto3.client(
        "s3",
        aws_access_key_id=getattr(settings, "AWS_ACCESS_KEY_ID", None) or None,
        aws_secret_access_key=getattr(settings, "AWS_SECRET_ACCESS_KEY", None) or None,
        endpoint_url=getattr(settings, "AWS_S3_ENDPOINT_URL", None) or None,
        region_name=getattr(settings, "AWS_S3_REGION_NAME", None) or None,
    )

    url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": key},
        ExpiresIn=300,
    )
    return redirect(url)


@login_required
@paid_required
@require_http_methods(["POST"])
def document_delete(request: HttpRequest, document_id: str) -> HttpResponse:
    if request.user.organization_id is None:
        return render(request, "documents/no_org.html", status=400)

    doc = get_object_or_404(Document, id=document_id, organization_id=request.user.organization_id)
    AuditEvent.objects.create(
        organization_id=request.user.organization_id,
        user_id=request.user.id,
        event_type="document.deleted",
        payload={"document_id": str(doc.id), "filename": doc.filename},
    )
    doc.file.delete(save=False)
    doc.delete()
    return redirect("documents:index")

