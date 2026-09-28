from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, conint


class RootInfo(BaseModel):
    name: str
    version: str


class HealthResponse(BaseModel):
    status: str
    phase: int
    retriever_loaded: bool
    embedding_model_loaded: bool
    timestamp: str


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: Optional[conint(gt=0)] = Field(5)  # type: ignore[valid-type]


class SourceItem(BaseModel):
    conversation_id: str
    similarity_score: float


class ChatResponse(BaseModel):
    query: str
    detected_intent: str
    answer: str
    confidence: float
    sources: List[SourceItem]
    conversation_turn: int
    escalation_decision: Optional[str] = None
    escalation_priority: Optional[str] = None
    escalation_reason: Optional[str] = None
    escalation_triggered: bool = False


class ResetResponse(BaseModel):
    status: str
