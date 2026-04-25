from __future__ import annotations

from typing import Any

from django.http import HttpRequest


def org_context(request: HttpRequest) -> dict[str, Any]:
    user = getattr(request, "user", None)
    org = getattr(user, "organization", None) if user and getattr(user, "is_authenticated", False) else None
    return {"current_org": org}

