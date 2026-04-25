from __future__ import annotations

import html
from collections.abc import Iterable

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from apps.chat.models import Chat, Message
from apps.chat.openai_chat import stream_chat_completion
from apps.rag.retrieval import retrieve_chunks
from apps.audit.models import AuditEvent
from apps.billing.decorators import paid_required


@login_required
@paid_required
def chat_home(request: HttpRequest) -> HttpResponse:
    if request.user.organization_id is None:
        return redirect("web:dashboard")

    chat = (
        Chat.objects.filter(organization_id=request.user.organization_id, created_by_id=request.user.id)
        .order_by("-created_at")
        .first()
    )
    if not chat:
        chat = Chat.objects.create(organization_id=request.user.organization_id, created_by_id=request.user.id, title="")
    return redirect("chat:detail", chat_id=str(chat.id))


@login_required
@paid_required
def chat_detail(request: HttpRequest, chat_id: str) -> HttpResponse:
    if request.user.organization_id is None:
        return redirect("web:dashboard")

    chat = get_object_or_404(
        Chat,
        id=chat_id,
        organization_id=request.user.organization_id,
        created_by_id=request.user.id,
    )
    messages = Message.objects.filter(chat_id=chat.id, organization_id=request.user.organization_id).order_by("created_at")
    chats = (
        Chat.objects.filter(organization_id=request.user.organization_id, created_by_id=request.user.id)
        .order_by("-created_at")[:25]
    )
    return render(request, "chat/detail.html", {"chat": chat, "messages": messages, "chats": chats})


def _build_prompt(question: str, retrieved) -> str:
    context_lines: list[str] = []
    for i, ch in enumerate(retrieved, start=1):
        context_lines.append(f"[{i}] ({ch.source_filename}) {ch.content}")

    context = "\n\n".join(context_lines)
    if context:
        return (
            "You are a helpful assistant. Use the context to answer. If the context is insufficient, say so.\n\n"
            f"Context:\n{context}\n\nQuestion:\n{question}\n"
        )
    return question


@login_required
@paid_required
@require_http_methods(["POST"])
def send_message(request: HttpRequest, chat_id: str) -> HttpResponse:
    if request.user.organization_id is None:
        return HttpResponse("No organization", status=400)

    chat = get_object_or_404(
        Chat,
        id=chat_id,
        organization_id=request.user.organization_id,
        created_by_id=request.user.id,
    )

    question = (request.POST.get("message") or "").strip()
    if not question:
        return HttpResponse("", status=400)

    Message.objects.create(
        organization_id=request.user.organization_id,
        chat_id=chat.id,
        role=Message.Role.USER,
        content=question,
    )
    AuditEvent.objects.create(
        organization_id=request.user.organization_id,
        user_id=request.user.id,
        event_type="chat.message_sent",
        payload={"chat_id": str(chat.id)},
    )

    retrieved = retrieve_chunks(request.user.organization_id, question, k=6)
    prompt = _build_prompt(question, retrieved)

    def gen() -> Iterable[bytes]:
        # First, add the user message HTML (so HTMX can swap in one response)
        yield render(request, "chat/partials/user_message.html", {"content": question}).content

        # Then, stream the assistant message container + incremental chunks
        yield render(request, "chat/partials/assistant_message_start.html", {"citations": retrieved}).content
        for token in stream_chat_completion(prompt):
            safe = html.escape(token)
            yield safe.encode("utf-8")
        yield render(request, "chat/partials/assistant_message_end.html").content

    return StreamingHttpResponse(gen(), content_type="text/html; charset=utf-8")

