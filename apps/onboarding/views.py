from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.billing.decorators import paid_required
from apps.documents.models import Document


@login_required
@paid_required
def start(request: HttpRequest) -> HttpResponse:
    org_id = request.user.organization_id
    docs = Document.objects.filter(organization_id=org_id).order_by("-created_at")[:10]
    ready_count = Document.objects.filter(organization_id=org_id, status=Document.Status.READY).count()
    total_count = Document.objects.filter(organization_id=org_id).count()

    has_ready = ready_count > 0
    return render(
        request,
        "onboarding/start.html",
        {
            "documents": docs,
            "ready_count": ready_count,
            "total_count": total_count,
            "has_ready": has_ready,
        },
    )


@login_required
@paid_required
def go_chat(request: HttpRequest) -> HttpResponse:
    return redirect("chat:home")

