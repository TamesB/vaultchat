from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from apps.audit.models import AuditEvent
from apps.orgs.forms import OrganizationCreateForm


@login_required
@require_http_methods(["GET", "POST"])
def create_org(request: HttpRequest) -> HttpResponse:
    if request.user.organization_id:
        return redirect("web:dashboard")

    if request.method == "POST":
        form = OrganizationCreateForm(request.POST)
        if form.is_valid():
            org = form.save()
            request.user.organization = org
            request.user.save(update_fields=["organization"])

            AuditEvent.objects.create(
                organization_id=org.id,
                user_id=request.user.id,
                event_type="org.created",
                payload={"organization_id": str(org.id)},
            )

            return redirect("pilots:intake")
    else:
        form = OrganizationCreateForm()

    return render(request, "orgs/create.html", {"form": form})

