import uuid

from django.db import models


class Organization(models.Model):
    class BillingStatus(models.TextChoices):
        TRIAL_LOCKED = "trial_locked", "Trial locked"
        PAID = "paid", "Paid"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    billing_status = models.CharField(
        max_length=32,
        choices=BillingStatus.choices,
        default=BillingStatus.TRIAL_LOCKED,
    )
    stripe_customer_id = models.CharField(max_length=255, blank=True, default="")
    stripe_checkout_session_id = models.CharField(max_length=255, blank=True, default="")
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name

