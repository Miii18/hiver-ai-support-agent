from __future__ import annotations

from typing import Any


class ResponseFormatter:
    """Formats the final chatbot response as a clean JSON-like dictionary."""

    @staticmethod
    def format_response(
        answer: str,
        intent_label: str,
        intent_category: str,
        confidence: float,
        context: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return {
            'answer': str(answer).strip(),
            'intent_label': str(intent_label),
            'intent_category': str(intent_category),
            'confidence': float(confidence),
            'context': [dict(item) for item in context],
        }
