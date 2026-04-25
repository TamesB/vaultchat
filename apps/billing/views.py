from __future__ import annotations

import stripe
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.audit.models import AuditEvent
from apps.orgs.models import Organization


def _stripe_config() -> None:
    stripe.api_key = settings.STRIPE_SECRET_KEY or None


def _require_org(request: HttpRequest) -> Organization:
    org = getattr(request.user, "organization", None)
    if not org:
        raise ValueError("User has no organization")
    return org


@require_http_methods(["GET"])
def pay(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect(settings.LOGIN_URL)

    org = _require_org(request)
    if org.billing_status == Organization.BillingStatus.PAID:
        return redirect("onboarding:start")

    return render(request, "billing/pay.html", {"organization": org})


@require_http_methods(["POST"])
def start_checkout(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect(settings.LOGIN_URL)

    org = _require_org(request)
    if org.billing_status == Organization.BillingStatus.PAID:
        return redirect("onboarding:start")

    if not settings.STRIPE_SECRET_KEY or not settings.STRIPE_PILOT_PRICE_ID:
        return HttpResponse("Stripe is not configured", status=500)

    _stripe_config()

    customer_id = org.stripe_customer_id
    if not customer_id:
        customer = stripe.Customer.create(
            name=org.name,
            email=request.user.email,
            metadata={"organization_id": str(org.id)},
        )
        customer_id = customer["id"]
        org.stripe_customer_id = customer_id
        org.save(update_fields=["stripe_customer_id"])

    session = stripe.checkout.Session.create(
        mode="payment",
        customer=customer_id,
        line_items=[{"price": settings.STRIPE_PILOT_PRICE_ID, "quantity": 1}],
        success_url=settings.STRIPE_SUCCESS_URL,
        cancel_url=settings.STRIPE_CANCEL_URL,
        metadata={"organization_id": str(org.id)},
    )

    org.stripe_checkout_session_id = session["id"]
    org.save(update_fields=["stripe_checkout_session_id"])

    AuditEvent.objects.create(
        organization_id=org.id,
        user_id=request.user.id,
        event_type="billing.checkout_started",
        payload={"checkout_session_id": session["id"]},
    )

    return redirect(session["url"])


@require_http_methods(["GET"])
def success(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect(settings.LOGIN_URL)
    return render(request, "billing/success.html")


@require_http_methods(["GET"])
def cancel(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect(settings.LOGIN_URL)
    return render(request, "billing/cancel.html")


@csrf_exempt
@require_http_methods(["POST"])
def webhook(request: HttpRequest) -> HttpResponse:
    if not settings.STRIPE_WEBHOOK_SECRET:
        return HttpResponse("Webhook not configured", status=500)

    _stripe_config()

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    try:
        event = stripe.Webhook.construct_event(payload=payload, sig_header=sig_header, secret=settings.STRIPE_WEBHOOK_SECRET)
    except Exception:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        org_id = (session.get("metadata") or {}).get("organization_id")
        checkout_id = session.get("id", "")
        customer_id = session.get("customer", "")

        org = None
        if org_id:
            org = Organization.objects.filter(id=org_id).first()
        if not org and checkout_id:
            org = Organization.objects.filter(stripe_checkout_session_id=checkout_id).first()
        if org and org.billing_status != Organization.BillingStatus.PAID:
            org.billing_status = Organization.BillingStatus.PAID
            org.paid_at = timezone.now()
            if customer_id and not org.stripe_customer_id:
                org.stripe_customer_id = customer_id
            org.save(update_fields=["billing_status", "paid_at", "stripe_customer_id"])

            AuditEvent.objects.create(
                organization_id=org.id,
                user=None,
                event_type="billing.paid",
                payload={"checkout_session_id": checkout_id, "customer_id": customer_id},
            )

    return HttpResponse(status=200)

