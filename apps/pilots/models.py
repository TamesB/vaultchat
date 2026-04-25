from __future__ import annotations

import uuid

from django.db import models

from apps.orgs.models import Organization


class PilotIntake(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="pilot_intakes")

    contact_name = models.CharField(max_length=255)
    contact_email = models.EmailField()

    use_case = models.TextField()
    doc_types = models.TextField(blank=True, default="")
    success_criteria = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

