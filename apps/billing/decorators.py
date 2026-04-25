from __future__ import annotations

from collections.abc import Callable
from functools import wraps

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

from apps.orgs.models import Organization


def paid_required(view_func: Callable[..., HttpResponse]):
    @wraps(view_func)
    def _wrapped(request: HttpRequest, *args, **kwargs):
        org = getattr(request.user, "organization", None)
        if not org:
            return redirect("web:dashboard")
        if org.billing_status != Organization.BillingStatus.PAID:
            return redirect("billing:pay")
        return view_func(request, *args, **kwargs)

    return _wrapped

