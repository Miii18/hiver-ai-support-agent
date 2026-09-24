from __future__ import annotations

import logging
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from src.api.schemas import (
    RootInfo,
    HealthResponse,
    ChatRequest,
    ChatResponse,
    ResetResponse,
    SourceItem,
)
from src.api.dependencies import get_chatbot_singleton

LOGGER = logging.getLogger('api.routes')

router = APIRouter()


@router.get('/', response_model=RootInfo)
def root(info: dict = Depends(get_chatbot_singleton)) -> RootInfo:
    from src.api.config import settings

    LOGGER.info('Root metadata requested')
    return RootInfo(name=settings.project_name, version=settings.version)


@router.get('/health', response_model=HealthResponse)
def health(info: dict = Depends(get_chatbot_singleton)) -> HealthResponse:
    retriever = info.get('retriever_state')
    retriever_loaded = retriever is not None
    embedding_model_loaded = retriever_loaded and retriever.get('model') is not None
    return HealthResponse(
        status='healthy' if retriever_loaded else 'degraded',
        phase=8,
        retriever_loaded=retriever_loaded,
        embedding_model_loaded=bool(embedding_model_loaded),
        timestamp=datetime.utcnow().isoformat() + 'Z',
    )


@router.get('/intents')
def intents(info: dict = Depends(get_chatbot_singleton)) -> dict:
    try:
        classifier = info['chatbot'].classifier
        catalog = classifier.intent_catalog
        return {"intents": catalog.to_dict(orient='records')}
    except Exception:
        LOGGER.exception('Failed to load intents')
        raise HTTPException(status_code=500, detail='Intent catalog unavailable')


@router.post('/chat', response_model=ChatResponse)
def chat(req: ChatRequest, info: dict = Depends(get_chatbot_singleton)) -> ChatResponse:
    if not req.query.strip():
        raise HTTPException(status_code=400, detail='Query must not be empty')
    if req.top_k is not None and req.top_k <= 0:
        raise HTTPException(status_code=400, detail='top_k must be positive')

    bot = info['chatbot']
    try:
        start = datetime.utcnow()
        resp = bot.answer_query(req.query)
        elapsed = (datetime.utcnow() - start).total_seconds()
        LOGGER.info('Chat request processed in %.3fs', elapsed)
    except Exception as exc:
        LOGGER.exception('Error processing chat request: %s', exc)
        raise HTTPException(status_code=500, detail='Error generating response')

    sources = [
        SourceItem(conversation_id=item.get('conversation_id', ''), similarity_score=float(item.get('similarity_score', 0.0)))
        for item in resp.get('context', [])
    ]

    # robustly compute conversation turn from various memory implementations
    mem = getattr(bot, 'memory', None)
    conversation_turn = 0
    if mem is None:
        conversation_turn = 0
    elif hasattr(mem, 'summarize'):
        try:
            conversation_turn = int(mem.summarize().get('turn_count', 0))
        except Exception:
            conversation_turn = 0
    elif hasattr(mem, 'history'):
        try:
            conversation_turn = len(getattr(mem, 'history') or [])
        except Exception:
            conversation_turn = 0
    else:
        try:
            conversation_turn = int(len(mem))
        except Exception:
            conversation_turn = 0

    escalation = resp.get('escalation') or {}
    return ChatResponse(
        query=req.query,
        detected_intent=resp.get('intent_label', ''),
        answer=resp.get('answer', ''),
        confidence=float(resp.get('confidence', 0.0)),
        sources=sources,
        conversation_turn=int(conversation_turn),
        escalation_decision=escalation.get('escalation_decision'),
        escalation_priority=escalation.get('escalation_priority'),
        escalation_reason=escalation.get('escalation_reason'),
        escalation_triggered=bool(resp.get('escalation_triggered', False)),
    )


@router.post('/reset', response_model=ResetResponse)
def reset(info: dict = Depends(get_chatbot_singleton)) -> ResetResponse:
    bot = info['chatbot']
    try:
        bot.memory.history = []
    except Exception:
        setattr(bot, 'memory', [])
    LOGGER.info('Conversation memory reset')
    return ResetResponse(status='memory_reset')
