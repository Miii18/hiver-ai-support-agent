"""Dependency injection and singletons for API services."""
from __future__ import annotations

from pathlib import Path
from typing import Any
import logging
import threading

logger = logging.getLogger(__name__)

# Simple thread-safe singleton container
_lock = threading.Lock()
_instances = {}


class DummyChatbot:
    """Fallback chatbot when project components are unavailable.

    Methods implemented to match expected interface used by the API.
    """

    def __init__(self):
        self.memory = []

    def classify_intent(self, query: str) -> str:
        return "general_inquiry"

    def embed(self, texts: list[str]) -> list[list[float]]:
        # return small deterministic vectors
        return [[float(len(t) % 10)] for t in texts]

    def retrieve(self, embedding: list[float], top_k: int = 5) -> list[dict]:
        # return dummy sources
        return [{"source": "example_source", "score": 0.9}]

    def build_prompt(self, query: str, contexts: list[dict]) -> str:
        return f"Answer the query: {query}\nContext: {contexts[:1]}"

    def generate(self, prompt: str) -> tuple[str, float]:
        return ("This is a dummy answer.", 0.75)

    def reset_memory(self) -> None:
        self.memory = []


def get_chatbot() -> Any:
    """Return a singleton chatbot instance, attempting to import the real one if available."""
    with _lock:
        if 'chatbot' in _instances:
            return _instances['chatbot']

        try:
            # attempt to import project chatbot (do not fail if missing)
            from src.chatbot import Chatbot  # type: ignore

            inst = Chatbot()
            logger.info("Loaded project Chatbot implementation")
        except Exception:
            logger.warning("Project Chatbot not available; using DummyChatbot")
            inst = DummyChatbot()

        _instances['chatbot'] = inst
        return inst


def get_intents() -> list[dict]:
    """Return a list of intents from project taxonomy if available, else sample intents."""
    try:
        from src.taxonomy import load_intents  # type: ignore

        return load_intents()
    except Exception:
        logger.warning('Taxonomy not available; returning sample intents')
        return [
            {"id": 1, "name": "Delivery Issue", "description": "Problems with delivery or tracking."},
            {"id": 2, "name": "Refund", "description": "Refund and payment queries."},
        ]
import logging
from functools import lru_cache
from typing import Any

from src.chatbot.chatbot import SupportChatbot
from src.retrieval.retriever import load_index

LOGGER = logging.getLogger('api.dependencies')


@lru_cache(maxsize=1)
def get_chatbot_singleton() -> dict[str, Any]:
    """Initialize and cache chatbot and retrieval artifacts."""
    LOGGER.info('Initializing chatbot singleton and loading retriever/index...')
    bot = SupportChatbot()
    retriever_state = None
    try:
        retriever_state = load_index()
        LOGGER.info('Retriever loaded: %d documents', len(retriever_state.get('documents')))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.exception('Failed to load FAISS index or embeddings: %s', exc)
    return {'chatbot': bot, 'retriever_state': retriever_state}
