#!/usr/bin/env python
"""Phase 9.5 Intelligence Upgrade - Standalone validation (no FAISS dependency)."""
import re
from typing import Optional, Tuple


class IntelligenceHandler:
    """Handles meta queries about the AI system without retrieval."""

    IDENTITY_PATTERNS = {
        "who_are_you": r"(who\s+are\s+you|who\s+is\s+this|introduce\s+yourself)",
        "what_are_you": r"(what\s+are\s+you|what\s+is\s+this)",
        "tell_about_yourself": r"(tell\s+me\s+about\s+yourself|about\s+yourself)",
        "are_you_ai": r"(are\s+you\s+an?\s+ai|are\s+you\s+artificial)",
    }

    CAPABILITY_PATTERNS = {
        "what_can_help": r"(what\s+can\s+you\s+help\s+me\s+with|what\s+can\s+you\s+do|what\s+features|what\s+support)",
    }

    KNOWLEDGE_BASE_PATTERNS = {
        "knowledge_base": r"(knowledge\s+base|trained|training\s+data|what\s+data)",
    }

    CONFIDENCE_PATTERNS = {
        "confidence_score": r"(confidence\s+score|confidence|how\s+confident|why.*low)",
    }

    SOURCES_PATTERNS = {
        "show_sources": r"(show.*source|previous\s+source|what\s+source|retrieved)",
    }

    OUT_OF_SCOPE_PATTERNS = {
        "joke": r"(tell\s+me\s+a\s+joke|joke)",
        "weather": r"(weather|temperature|forecast)",
        "code": r"(write\s+code|write\s+python)",
    }

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for pattern matching."""
        return text.lower().strip()

    @classmethod
    def detect_ai_identity(cls, query: str) -> bool:
        """Detect if query asks about AI identity."""
        normalized = cls.normalize_text(query)
        for pattern in cls.IDENTITY_PATTERNS.values():
            if re.search(pattern, normalized):
                return True
        return False

    @classmethod
    def detect_capability_query(cls, query: str) -> bool:
        """Detect if query asks about capabilities."""
        normalized = cls.normalize_text(query)
        for pattern in cls.CAPABILITY_PATTERNS.values():
            if re.search(pattern, normalized):
                return True
        return False

    @classmethod
    def detect_knowledge_base_query(cls, query: str) -> bool:
        """Detect if query asks about knowledge base."""
        normalized = cls.normalize_text(query)
        for pattern in cls.KNOWLEDGE_BASE_PATTERNS.values():
            if re.search(pattern, normalized):
                return True
        return False

    @classmethod
    def detect_confidence_query(cls, query: str) -> bool:
        """Detect if query asks about confidence."""
        normalized = cls.normalize_text(query)
        for pattern in cls.CONFIDENCE_PATTERNS.values():
            if re.search(pattern, normalized):
                return True
        return False

    @classmethod
    def detect_sources_query(cls, query: str) -> bool:
        """Detect if query asks about sources."""
        normalized = cls.normalize_text(query)
        for pattern in cls.SOURCES_PATTERNS.values():
            if re.search(pattern, normalized):
                return True
        return False

    @classmethod
    def detect_out_of_scope(cls, query: str) -> bool:
        """Detect if query is outside Amazon support scope."""
        normalized = cls.normalize_text(query)
        for pattern in cls.OUT_OF_SCOPE_PATTERNS.values():
            if re.search(pattern, normalized):
                return True
        return False


# Test queries
TEST_QUERIES = [
    ("Who are you?", "AI Identity", True),
    ("What can you help me with?", "Capability", True),
    ("What is your knowledge base?", "Knowledge Base", True),
    ("What is your confidence score?", "Confidence", True),
    ("Show retrieved sources.", "Sources", True),
    ("Tell me a joke.", "Out of Scope", True),
    ("My Amazon package has not been delivered.", "Support Query", False),
]


def main():
    """Run validation."""
    print("\n" + "=" * 80)
    print("PHASE 9.5 INTELLIGENCE UPGRADE VALIDATION")
    print("=" * 80 + "\n")

    handler = IntelligenceHandler()
    all_passed = True
    results = []

    for query, query_type, should_handle in TEST_QUERIES:
        is_meta = (
            handler.detect_ai_identity(query)
            or handler.detect_capability_query(query)
            or handler.detect_knowledge_base_query(query)
            or handler.detect_confidence_query(query)
            or handler.detect_sources_query(query)
            or handler.detect_out_of_scope(query)
        )

        passed = is_meta == should_handle
        status = "PASS" if passed else "FAIL"
        results.append((status, query, query_type, "Meta" if is_meta else "Support"))

        if not passed:
            all_passed = False

    # Print results table
    for status, query, expected_type, detected_type in results:
        print(f"[{status}] {query:45s} -> {expected_type:20s} [{detected_type}]")

    print("\n" + "=" * 80)

    if all_passed:
        print("PHASE 9.5 INTELLIGENCE UPGRADE COMPLETED")
        return 0
    else:
        print("PHASE 9.5 INTELLIGENCE UPGRADE FAILED")
        return 1


if __name__ == "__main__":
    exit(main())
