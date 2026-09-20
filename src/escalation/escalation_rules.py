"""Escalation rules for the production escalation engine."""
from __future__ import annotations

import re
from typing import Optional


class EscalationRules:
    """Rules engine for escalation decisions."""

    # Critical escalation triggers (account security, fraud, legal)
    CRITICAL_PATTERNS = [
        r"account.*hacked",
        r"fraud",
        r"scam",
        r"stolen",
        r"charge.*twice",
        r"unauthorized.*charge",
        r"dispute",
        r"chargeback",
        r"legal",
        r"lawsuit",
        r"threat",
        r"emergency",
    ]

    # High priority escalation triggers (high-value issues, pending refunds)
    HIGH_PRIORITY_PATTERNS = [
        r"refund.*pending.*long",
        r"refund.*waiting.*month",
        r"missing.*package.*expensive",
        r"missing.*\$[0-9]{3,}",
        r"expensive.*item.*missing",
        r"high.*value.*package",
        r"account.*locked.*long",
    ]

    # Auto-handleable intents
    AUTO_HANDLE_INTENTS = {
        "Greeting": 1.0,
        "Delivery": 0.8,
        "Orders": 0.8,
        "Promotions & Coupons": 0.7,
        "Login & Authentication": 0.85,
        "Prime Membership": 0.75,
        "Technical Issue": 0.7,
    }

    @classmethod
    def check_critical_triggers(cls, query: str) -> Optional[str]:
        """Check for critical escalation triggers. Returns reason if found."""
        normalized = query.lower()
        for pattern in cls.CRITICAL_PATTERNS:
            if re.search(pattern, normalized):
                return f"Critical issue detected: {pattern}"
        return None

    @classmethod
    def check_high_priority_triggers(cls, query: str) -> Optional[str]:
        """Check for high-priority escalation triggers. Returns reason if found."""
        normalized = query.lower()
        for pattern in cls.HIGH_PRIORITY_PATTERNS:
            if re.search(pattern, normalized):
                return f"High-priority issue detected: {pattern}"
        return None

    @classmethod
    def can_auto_handle(cls, intent: str, confidence: float) -> bool:
        """Check if query can be auto-handled based on intent and confidence."""
        if intent not in cls.AUTO_HANDLE_INTENTS:
            return False

        required_confidence = cls.AUTO_HANDLE_INTENTS[intent]
        return confidence >= required_confidence
