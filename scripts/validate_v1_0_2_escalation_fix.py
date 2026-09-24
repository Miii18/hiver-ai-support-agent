"""Validation script for Version 1.0.2 — Escalation Response Fix."""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import re

from src.escalation.escalation_rules import EscalationRules
from src.chatbot.response_template_builder import ResponseTemplateBuilder

BANNED_PATTERNS = [
    r"account\.\*hacked",
    r"charge\.\*twice",
    r"EscalationPriority\.CRITICAL",
    r"EscalationPriority\.MEDIUM",
]

TEST_CASES = [
    {
        "query": "My account was hacked",
        "expected_type": "security",
        "expected_label": "Escalation Required — Account Security",
        "expected_priority_raw": "CRITICAL",
    },
    {
        "query": "I was charged twice",
        "expected_type": "billing",
        "expected_label": "Escalation Required — Billing Investigation",
        "expected_priority_raw": "CRITICAL",
    },
    {
        "query": "My refund has been pending for 45 days",
        "expected_type": "refund",
        "expected_label": "Refund Investigation",
        "expected_priority_raw": "CRITICAL",
    },
    {
        "query": "Received torn packet",
        "expected_type": "damaged",
        "expected_label": "Damaged Item Report",
        "expected_priority_raw": "CRITICAL",
    },
]


def check_no_banned_text(text: str) -> list[str]:
    violations = []
    for pat in BANNED_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            violations.append(pat)
    return violations


def run_validation() -> None:
    rules = EscalationRules()
    passed = 0

    for case in TEST_CASES:
        query = case["query"]
        esc_type, friendly_reason = ResponseTemplateBuilder.classify_escalation_type(
            query=query, intent="", raw_reason=""
        )
        cfg = ResponseTemplateBuilder.BANNER_CONFIG.get(esc_type, ResponseTemplateBuilder.BANNER_CONFIG["general"])

        # Check escalation rules don't leak regex
        reason_from_rules = rules.check_critical_triggers(query) or rules.check_high_priority_triggers(query) or ""
        banned_in_rules = check_no_banned_text(reason_from_rules)
        banned_in_label = check_no_banned_text(cfg["label"])
        banned_in_reason = check_no_banned_text(cfg["friendly_reason"])

        ok = (
            esc_type == case["expected_type"]
            and cfg["label"] == case["expected_label"]
            and not banned_in_rules
            and not banned_in_label
            and not banned_in_reason
        )

        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {query}")
        if not ok:
            if esc_type != case["expected_type"]:
                print(f"       type: expected={case['expected_type']} got={esc_type}")
            if cfg["label"] != case["expected_label"]:
                print(f"       label: expected={case['expected_label']!r} got={cfg['label']!r}")
            for violation in banned_in_rules + banned_in_label + banned_in_reason:
                print(f"       BANNED TEXT: {violation}")
        else:
            passed += 1

    print()
    if passed == len(TEST_CASES):
        print("VERSION 1.0.2 ESCALATION RESPONSE FIX PASSED")
    else:
        print(f"FAILED: {passed}/{len(TEST_CASES)} cases passed")
        sys.exit(1)


if __name__ == "__main__":
    run_validation()
