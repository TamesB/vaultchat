from __future__ import annotations

from django.conf import settings
from openai import OpenAI


def get_openai_client() -> OpenAI:
    return OpenAI(api_key=settings.OPENAI_API_KEY or None)

