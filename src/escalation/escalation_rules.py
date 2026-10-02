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

    # High priority escalation triggers (high-value issues, pending refunds, damaged goods)
    HIGH_PRIORITY_PATTERNS = [
        r"refund.*pending.*long",
        r"refund.*waiting.*month",
        r"missing.*package.*expensive",
        r"missing.*\$[0-9]{3,}",
        r"expensive.*item.*missing",
        r"high.*value.*package",
        r"account.*locked.*long",
        r"damaged",
        r"defective",
        r"broken",
        r"cracked",
        r"shattered",
    ]

    # Auto-handleable intents
    AUTO_HANDLE_INTENTS = {
        "Greeting": 1.0,
        "Delivery": 0.8,
        "Orders": 0.8,
        "Returns & Refunds": 0.8,
        "Promotions & Coupons": 0.7,
        "Login & Authentication": 0.85,
        "Prime Membership": 0.75,
        "Technical Issue": 0.7,
        "Update Delivery Address": 0.8,
        "Exchange Request": 0.8,
        "Payment Failed — Money Still Deducted": 0.8,
        "Wrong Item Received": 0.8,
        "Delivery Partner Contact": 0.8,
        "Damaged Item Report": 0.8,
        "Damaged Product": 0.8,
        "Out of Scope": 0.8,
        "System Info": 0.8,
        "Other Support": 0.8,
    }

    @classmethod
    def check_critical_triggers(cls, query: str) -> Optional[str]:
        """Check for critical escalation triggers. Returns reason if found."""
        normalized = query.lower()
        for pattern in cls.CRITICAL_PATTERNS:
            if re.search(pattern, normalized):
                return "Critical issue detected."
        return None

    @classmethod
    def check_high_priority_triggers(cls, query: str) -> Optional[str]:
        """Check for high-priority escalation triggers. Returns reason if found."""
        normalized = query.lower()
        for pattern in cls.HIGH_PRIORITY_PATTERNS:
            if re.search(pattern, normalized):
                return "High-priority issue detected."
        return None

    @classmethod
    def can_auto_handle(cls, intent: str, confidence: float) -> bool:
        """Check if query can be auto-handled based on intent and confidence."""
        if intent not in cls.AUTO_HANDLE_INTENTS:
            return False

        required_confidence = cls.AUTO_HANDLE_INTENTS[intent]
        return confidence >= required_confidence
