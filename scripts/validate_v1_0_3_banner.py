"""Validation script for Version 1.0.3 — Streamlit Escalation Banner."""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.chatbot.response_template_builder import ResponseTemplateBuilder

TEST_CASES = [
    {
        "query": "My account was hacked",
        "expected_type": "security",
        "expected_label": "Escalation Required — Account Security",
        "expected_icon": "🔴",
        "expected_reason": "Possible account compromise detected.",
    },
    {
        "query": "I was charged twice",
        "expected_type": "billing",
        "expected_label": "Escalation Required — Billing Investigation",
        "expected_icon": "🟠",
        "expected_reason": "A duplicate charge was detected.",
    },
    {
        "query": "My refund has been pending for 45 days",
        "expected_type": "refund",
        "expected_label": "Refund Investigation",
        "expected_icon": "🔵",
        "expected_reason": "Refund investigation required.",
    },
    {
        "query": "Received torn packet",
        "expected_type": "damaged",
        "expected_label": "Damaged Item Report",
        "expected_icon": "🟡",
        "expected_reason": "Your package appears damaged during delivery.",
    },
]

BANNED = ["EscalationPriority", "account.*hacked", "charge.*twice"]


def run_validation() -> None:
    passed = 0
    for case in TEST_CASES:
        query = case["query"]
        esc_type, _ = ResponseTemplateBuilder.classify_escalation_type(
            query=query, intent="", raw_reason=""
        )
        cfg = ResponseTemplateBuilder.BANNER_CONFIG.get(esc_type, ResponseTemplateBuilder.BANNER_CONFIG["general"])

        checks = {
            "type": esc_type == case["expected_type"],
            "label": cfg["label"] == case["expected_label"],
            "icon": cfg["icon"] == case["expected_icon"],
            "reason": cfg["friendly_reason"] == case["expected_reason"],
            "no_banned": not any(b in str(cfg) for b in BANNED),
        }
        ok = all(checks.values())
        print(f"[{'PASS' if ok else 'FAIL'}] {query}")
        if not ok:
            for k, v in checks.items():
                if not v:
                    print(f"       {k}: expected={case.get('expected_'+k, '?')!r} got={cfg.get(k, esc_type if k=='type' else '?')!r}")
        else:
            passed += 1

    print()
    if passed == len(TEST_CASES):
        print("VERSION 1.0.3 STREAMLIT ESCALATION BANNER PASSED")
    else:
        print(f"FAILED: {passed}/{len(TEST_CASES)} cases passed")
        sys.exit(1)


if __name__ == "__main__":
    run_validation()
