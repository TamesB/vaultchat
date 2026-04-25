from __future__ import annotations

import uuid

from django.db import models

from apps.documents.models import Document
from apps.orgs.models import Organization
from pgvector.django import VectorField


class DocumentChunk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="document_chunks")
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="chunks")

    chunk_index = models.PositiveIntegerField()
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)

    embedding = VectorField(dimensions=1536)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("document", "chunk_index")]

