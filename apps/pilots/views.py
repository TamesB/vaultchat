from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from apps.orgs.models import Organization
from apps.pilots.forms import PilotIntakeForm
from apps.pilots.models import PilotIntake


@login_required
@require_http_methods(["GET", "POST"])
def intake(request: HttpRequest) -> HttpResponse:
    org = getattr(request.user, "organization", None)
    if not org:
        return redirect("orgs:create")

    if request.method == "POST":
        form = PilotIntakeForm(request.POST)
        if form.is_valid():
            PilotIntake.objects.create(organization=org, **form.cleaned_data)
            return redirect("billing:pay")
    else:
        form = PilotIntakeForm(
            initial={
                "contact_email": request.user.email,
            }
        )

    latest_intake = PilotIntake.objects.filter(organization_id=org.id).order_by("-created_at").first()
    return render(
        request,
        "pilots/intake.html",
        {
            "form": form,
            "organization": org,
            "billing_status": org.billing_status,
            "latest_intake": latest_intake,
            "is_paid": org.billing_status == Organization.BillingStatus.PAID,
        },
    )

