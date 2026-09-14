from __future__ import annotations

from typing import Any


class ConversationMemory:
    """Simple in-memory chat history for the support assistant."""

    def __init__(self, max_turns: int = 6) -> None:
        self.max_turns = max_turns
        self.history: list[dict[str, str]] = []

    def add_turn(self, role: str, content: str) -> None:
        entry = {'role': str(role).strip(), 'content': str(content).strip()}
        self.history.append(entry)
        if len(self.history) > self.max_turns:
            self.history = self.history[-self.max_turns :]

    def get_recent_context(self) -> list[dict[str, str]]:
        return [dict(item) for item in self.history]

    def summarize(self) -> dict[str, Any]:
        return {
            'turn_count': len(self.history),
            'last_turn': self.history[-1] if self.history else None,
        }
