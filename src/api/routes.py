from __future__ import annotations

import logging
from datetime import datetime

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


# -----------------------------
# Root endpoint
# -----------------------------
@router.get("/", response_model=RootInfo)
def root(info: dict = Depends(get_chatbot_singleton)) -> RootInfo:
    from src.api.config import settings

    LOGGER.info("Root endpoint called")

    return RootInfo(
        name=settings.project_name,
        version=settings.version,
    )


# -----------------------------
# Health endpoint
# -----------------------------
@router.get("/health", response_model=HealthResponse)
def health(info: dict = Depends(get_chatbot_singleton)) -> HealthResponse:
    retriever = info.get("retriever_state")

    retriever_loaded = retriever is not None
    embedding_model_loaded = (
        retriever_loaded and retriever.get("model") is not None
    )

    return HealthResponse(
        status="healthy" if retriever_loaded else "degraded",
        phase=8,
        retriever_loaded=retriever_loaded,
        embedding_model_loaded=embedding_model_loaded,
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


# -----------------------------
# Intent list
# -----------------------------
@router.get("/intents")
def intents(info: dict = Depends(get_chatbot_singleton)):
    try:
        classifier = info["chatbot"].classifier
        catalog = classifier.intent_catalog

        return {"intents": catalog.to_dict(orient="records")}

    except Exception:
        LOGGER.exception("Failed to load intents")
        raise HTTPException(
            status_code=500,
            detail="Intent catalog unavailable",
        )


# -----------------------------
# Chat endpoint
# -----------------------------
@router.post("/chat", response_model=ChatResponse)
def chat(
    req: ChatRequest,
    info: dict = Depends(get_chatbot_singleton),
) -> ChatResponse:

    if not req.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query must not be empty",
        )

    if req.top_k is not None and req.top_k <= 0:
        raise HTTPException(
            status_code=400,
            detail="top_k must be positive",
        )

    bot = info["chatbot"]

    try:
        start = datetime.utcnow()
        resp = bot.answer_query(req.query)
        elapsed = (datetime.utcnow() - start).total_seconds()

        LOGGER.info("Chat processed in %.2fs", elapsed)

    except Exception:
        LOGGER.exception("Chat request failed")
        raise HTTPException(
            status_code=500,
            detail="Error generating response",
        )

    sources = [
        SourceItem(
            conversation_id=item.get("conversation_id", ""),
            similarity_score=float(item.get("similarity_score", 0.0)),
        )
        for item in resp.get("context", [])
    ]

    # Conversation turn calculation
    conversation_turn = 0
    memory = getattr(bot, "memory", None)

    try:
        if memory is None:
            conversation_turn = 0
        elif hasattr(memory, "summarize"):
            conversation_turn = int(
                memory.summarize().get("turn_count", 0)
            )
        elif hasattr(memory, "history"):
            conversation_turn = len(memory.history or [])
        else:
            conversation_turn = len(memory)
    except Exception:
        conversation_turn = 0

    escalation = resp.get("escalation") or {}

    return ChatResponse(
        query=req.query,
        detected_intent=resp.get("intent_label", ""),
        answer=resp.get("answer", ""),
        confidence=float(resp.get("confidence", 0.0)),
        sources=sources,
        conversation_turn=conversation_turn,
        escalation_decision=escalation.get("escalation_decision"),
        escalation_priority=escalation.get("escalation_priority"),
        escalation_reason=escalation.get("escalation_reason"),
        escalation_triggered=bool(
            resp.get("escalation_triggered", False)
        ),
    )


# -----------------------------
# Reset conversation
# -----------------------------
@router.post("/reset", response_model=ResetResponse)
def reset(info: dict = Depends(get_chatbot_singleton)) -> ResetResponse:
    bot = info["chatbot"]

    try:
        bot.memory.history = []
    except Exception:
        setattr(bot, "memory", [])

    LOGGER.info("Conversation memory reset")

    return ResetResponse(status="memory_reset")