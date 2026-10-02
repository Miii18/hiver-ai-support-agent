from __future__ import annotations

import logging
import traceback
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import get_chatbot_singleton
from src.api.schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    ResetResponse,
    RootInfo,
    SourceItem,
)

LOGGER = logging.getLogger("api.routes")
router = APIRouter()


def _get_bot() -> dict:
    """Dependency wrapper that converts init failures to HTTP 503."""
    try:
        return get_chatbot_singleton()
    except RuntimeError as exc:
        tb = traceback.format_exc()
        LOGGER.error("routes: chatbot unavailable — %s\n%s", exc, tb)
        raise HTTPException(
            status_code=503,
            detail={"status": "error", "component": "chatbot", "message": str(exc)},
        )


# -----------------------------
# Root endpoint
# -----------------------------
@router.get("/", response_model=RootInfo)
def root() -> RootInfo:
    from src.api.config import settings

    return RootInfo(
        name=settings.project_name,
        version=settings.version,
    )


# -----------------------------
# Health endpoint
# -----------------------------
@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    from src.retrieval.retriever import _INDEX_CACHE, _MODEL_CACHE

    retriever_loaded = _INDEX_CACHE is not None
    embedding_loaded = _MODEL_CACHE is not None

    return HealthResponse(
        status="healthy",
        phase=9,
        retriever_loaded=retriever_loaded,
        embedding_model_loaded=embedding_loaded,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


# -----------------------------
# Intent list
# -----------------------------
@router.get("/intents")
def intents(info: dict = Depends(_get_bot)):
    try:
        classifier = info["chatbot"].classifier
        catalog = classifier.intent_catalog
        return {"intents": catalog.to_dict(orient="records")}
    except Exception as exc:
        LOGGER.exception("routes: failed to load intents")
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "component": "intent_classifier", "message": str(exc)},
        )


# -----------------------------
# Chat endpoint
# -----------------------------
@router.post("/chat", response_model=ChatResponse)
def chat(
    req: ChatRequest,
    info: dict = Depends(_get_bot),
) -> ChatResponse:

    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty")

    if req.top_k is not None and req.top_k <= 0:
        raise HTTPException(status_code=400, detail="top_k must be positive")

    bot = info["chatbot"]

    try:
        start = datetime.now(timezone.utc)
        LOGGER.info("chat: answer_query query=%r", req.query[:120])
        resp = bot.answer_query(req.query)
        elapsed = (datetime.now(timezone.utc) - start).total_seconds()
        LOGGER.info("chat: answer_query completed in %.2fs", elapsed)

    except Exception as exc:
        tb = traceback.format_exc()
        LOGGER.error(
            "chat: answer_query raised %s: %s\nTraceback:\n%s",
            type(exc).__name__, exc, tb,
        )
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "component": "answer_query",
                "message": f"{type(exc).__name__}: {exc}",
            },
        )

    sources = [
        SourceItem(
            conversation_id=item.get("conversation_id", ""),
            similarity_score=float(item.get("similarity_score", 0.0)),
        )
        for item in resp.get("context", [])
    ]

    conversation_turn = 0
    memory = getattr(bot, "memory", None)
    try:
        if memory is None:
            conversation_turn = 0
        elif hasattr(memory, "summarize"):
            conversation_turn = int(memory.summarize().get("turn_count", 0))
        elif hasattr(memory, "history"):
            conversation_turn = len(memory.history or [])
        else:
            conversation_turn = len(memory)
    except Exception:
        conversation_turn = 0

    escalation = resp.get("escalation") or {}
    escalation_triggered = bool(resp.get("escalation_triggered", False))
    escalation_decision = escalation.get("escalation_decision") or (
        "ESCALATE_TO_HUMAN" if escalation_triggered else "AUTO_HANDLE"
    )
    escalation_priority = escalation.get("escalation_priority") or (
        "HIGH" if escalation_triggered else "LOW"
    )
    escalation_reason = escalation.get("escalation_reason") or (
        "Human review required." if escalation_triggered else f"{resp.get('intent_label', 'Standard')} query handled automatically."
    )

    escalation_payload = {
        "escalation_decision": escalation_decision,
        "escalation_priority": escalation_priority,
        "escalation_reason": escalation_reason,
        "escalation_intent": resp.get("intent_label", ""),
    }

    return ChatResponse(
        query=req.query,
        detected_intent=resp.get("intent_label", ""),
        answer=resp.get("answer", ""),
        confidence=float(resp.get("confidence", 0.0)),
        sources=sources,
        conversation_turn=conversation_turn,
        escalation_decision=escalation_decision,
        escalation_priority=escalation_priority,
        escalation_reason=escalation_reason,
        escalation_triggered=escalation_triggered,
        escalation=escalation_payload,
    )


# -----------------------------
# Reset conversation
# -----------------------------
@router.post("/reset", response_model=ResetResponse)
def reset(info: dict = Depends(_get_bot)) -> ResetResponse:
    bot = info["chatbot"]

    try:
        bot.memory.history = []
    except Exception:
        setattr(bot, "memory", [])

    LOGGER.info("routes: conversation memory reset")
    return ResetResponse(status="memory_reset")
