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


def _build_prompt(question: str, retrieved, history=()) -> str:
    context_lines: list[str] = []
    for i, ch in enumerate(retrieved, start=1):
        context_lines.append(f"[{i}] ({ch.source_filename}) {ch.content}")

    context = "\n\n".join(context_lines)
    history_lines = [
        f"{message.role.capitalize()}: {message.content}"
        for message in history
    ]
    history_text = "\n\n".join(history_lines)

    instruction = "You are a helpful assistant. "
    if history_text:
        instruction += "Use the context and chat history to answer. "
    else:
        instruction += "Use the context to answer. "
    instruction += "If the context is insufficient, say so."
    prompt_sections = [instruction]
    if context:
        prompt_sections.append(f"Context:\n{context}")
    if history_text:
        prompt_sections.append(f"Chat history:\n{history_text}")
    if not context and not history_text:
        return question
    prompt_sections.append(f"Question:\n{question}")
    return "\n\n".join(prompt_sections) + "\n"


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

    history = list(
        Message.objects.filter(
            chat_id=chat.id,
            organization_id=request.user.organization_id,
        ).order_by("created_at")
    )
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
    prompt = _build_prompt(question, retrieved, history)

    print(prompt)

    def gen() -> Iterable[bytes]:
        answer_parts: list[str] = []

        # First, add the user message HTML (so HTMX can swap in one response)
        yield render(request, "chat/partials/user_message.html", {"content": question}).content

        # Then, stream the assistant message container + incremental chunks
        yield render(request, "chat/partials/assistant_message_start.html", {"citations": retrieved}).content
        try:
            for token in stream_chat_completion(prompt):
                answer_parts.append(token)
                safe = html.escape(token)
                yield safe.encode("utf-8")
        finally:
            final_answer = "".join(answer_parts).strip()
            if final_answer:
                Message.objects.create(
                    organization_id=request.user.organization_id,
                    chat_id=chat.id,
                    role=Message.Role.ASSISTANT,
                    content=final_answer,
                )
                if not chat.title:
                    chat.title = question[:80].strip() or "New chat"
                    chat.save(update_fields=["title"])

        yield render(request, "chat/partials/assistant_message_end.html").content

    return StreamingHttpResponse(gen(), content_type="text/html; charset=utf-8")
