from __future__ import annotations

from collections.abc import Iterator

from django.conf import settings

from openai import OpenAI


def stream_chat_completion(prompt: str) -> Iterator[str]:
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set")

    client = OpenAI(api_key=settings.OPENAI_API_KEY or None)
    stream = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    for event in stream:
        delta = event.choices[0].delta
        content = getattr(delta, "content", None)
        if content:
            yield content

