from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models

from apps.orgs.models import Organization


class Document(models.Model):
    class Status(models.TextChoices):
        UPLOADED = "uploaded", "Uploaded"
        PROCESSING = "processing", "Processing"
        READY = "ready", "Ready"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="documents")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="uploaded_documents")

    file = models.FileField(upload_to="documents/%Y/%m/%d/")
    filename = models.CharField(max_length=512)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.UPLOADED)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.filename

