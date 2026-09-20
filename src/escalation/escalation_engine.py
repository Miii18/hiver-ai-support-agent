"""Phase 10: Escalation Decision Engine - Core escalation logic."""
from __future__ import annotations

from enum import Enum
from typing import Any


class EscalationDecision(str, Enum):
    """Escalation decision values."""
    AUTO_HANDLE = "AUTO_HANDLE"
    ESCALATE_TO_HUMAN = "ESCALATE_TO_HUMAN"


class EscalationPriority(str, Enum):
    """Escalation priority levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EscalationEngine:
    """Production escalation decision engine."""

    def __init__(self):
        """Initialize escalation engine."""
        from src.escalation.escalation_rules import EscalationRules
        self.rules = EscalationRules()

    def decide(self, query: str, intent: str, confidence: float, context: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Make escalation decision based on query and intent.

        Returns dict with:
        - escalation_decision: AUTO_HANDLE or ESCALATE_TO_HUMAN
        - escalation_reason: explanation of decision
        - escalation_priority: LOW, MEDIUM, HIGH, or CRITICAL
        """
        # Check for critical escalation triggers first
        critical_triggers = self.rules.check_critical_triggers(query)
        if critical_triggers:
            return {
                "escalation_decision": EscalationDecision.ESCALATE_TO_HUMAN,
                "escalation_reason": critical_triggers,
                "escalation_priority": EscalationPriority.CRITICAL,
            }

        # Check for high-priority escalation triggers
        high_triggers = self.rules.check_high_priority_triggers(query)
        if high_triggers:
            return {
                "escalation_decision": EscalationDecision.ESCALATE_TO_HUMAN,
                "escalation_reason": high_triggers,
                "escalation_priority": EscalationPriority.HIGH,
            }

        # Check if intent can be auto-handled
        if self.rules.can_auto_handle(intent, confidence):
            return {
                "escalation_decision": EscalationDecision.AUTO_HANDLE,
                "escalation_reason": f"{intent} query with {confidence:.0%} confidence can be auto-handled.",
                "escalation_priority": EscalationPriority.LOW,
            }

        # Medium priority escalation
        return {
            "escalation_decision": EscalationDecision.ESCALATE_TO_HUMAN,
            "escalation_reason": f"Query requires human review. Intent: {intent}, Confidence: {confidence:.0%}",
            "escalation_priority": EscalationPriority.MEDIUM,
        }
