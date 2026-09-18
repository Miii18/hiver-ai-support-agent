from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class MetadataResponse(BaseModel):
    title: str
    version: str
    timestamp: datetime


class HealthResponse(BaseModel):
    status: str
    phase: int
    retriever_loaded: bool
    embedding_model_loaded: bool
    timestamp: datetime


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(5, ge=1, le=50)


class ChatResponse(BaseModel):
    query: str
    detected_intent: Optional[str]
    answer: str
    confidence: float
    sources: List[str]
    conversation_turn: int


class ResetResponse(BaseModel):
    status: str


class IntentItem(BaseModel):
    id: int
    name: str
    description: Optional[str]


class IntentsResponse(BaseModel):
    intents: List[IntentItem]

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
    top_k: Optional[conint(gt=0)] = Field(5)


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


class ResetResponse(BaseModel):
    status: str
