from __future__ import annotations

import sys
from pathlib import Path
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.api.app import app
from src.chatbot.chatbot import Chatbot

client = TestClient(app)
bot = Chatbot()

queries = [
    ("hi", "Greeting", "AUTO_HANDLE", False, "LOW"),
    ("hello", "Greeting", "AUTO_HANDLE", False, "LOW"),
    ("where is my order?", "Orders", "AUTO_HANDLE", False, "LOW"),
    ("I want to return my order.", "Returns & Refunds", "AUTO_HANDLE", False, "LOW"),
    ("I want a refund for my purchase.", "Returns & Refunds", "AUTO_HANDLE", False, "LOW"),
    ("I cannot login to my account.", "Login & Authentication", "AUTO_HANDLE", False, "LOW"),
    ("What is the weather today?", "Out of Scope", "AUTO_HANDLE", False, "LOW"),
    ("I received a damaged product.", "Damaged Item Report", "ESCALATE_TO_HUMAN", True, "HIGH"),
    ("My payment failed but money was deducted.", "Payment Failed — Money Still Deducted", "AUTO_HANDLE", False, "LOW"),
    ("Can I change my delivery address?", "Update Delivery Address", "AUTO_HANDLE", False, "LOW"),
    ("I received the wrong product and I want a refund immediately.", "Wrong Item Received", "AUTO_HANDLE", False, "LOW"),
    ("I want to exchange this product.", "Exchange Request", "AUTO_HANDLE", False, "LOW"),
    ("I want to contact the delivery agent.", "Delivery Partner Contact", "AUTO_HANDLE", False, "LOW"),
]

print("=== VERIFYING FASTAPI /chat AND CHATBOT FOR 13 CRITICAL QUERIES ===")
all_passed = True
results_table = []

for i, (q, exp_intent, exp_dec, exp_trig, exp_prio) in enumerate(queries, 1):
    # 1. API test via FastAPI /chat endpoint
    res = client.post("/chat", json={"query": q})
    assert res.status_code == 200, f"Status code {res.status_code}: {res.text}"
    api_data = res.json()

    api_answer = api_data.get("answer", "")
    api_intent = api_data.get("detected_intent")
    api_dec = api_data.get("escalation_decision")
    api_trig = api_data.get("escalation_triggered")
    api_prio = api_data.get("escalation_priority")
    api_esc = api_data.get("escalation") or {}

    # 2. Direct Chatbot test
    bot_resp = bot.answer_query(q)
    bot_esc = bot_resp.get("escalation") or {}
    bot_intent = bot_resp.get("intent_label")
    bot_trig = bot_resp.get("escalation_triggered")

    # Assertions
    c1_answer = bool(api_answer and len(api_answer.strip()) > 10)
    c2_intent = (api_intent == exp_intent)
    c3_dec = (api_dec == exp_dec)
    c4_trig = (api_trig == exp_trig)
    c5_prio = (api_prio == exp_prio)
    c6_api_esc_intent = (api_esc.get("escalation_intent") == api_intent)
    c7_api_esc_dec = (api_esc.get("escalation_decision") == api_dec)
    c8_api_esc_prio = (api_esc.get("escalation_priority") == api_prio)
    c9_direct_match = (
        bot_intent == api_intent
        and bot_trig == api_trig
        and bot_esc.get("escalation_decision") == api_dec
        and bot_esc.get("escalation_priority") == api_prio
        and bot_esc.get("escalation_intent") == api_intent
    )

    passed = (
        c1_answer
        and c2_intent
        and c3_dec
        and c4_trig
        and c5_prio
        and c6_api_esc_intent
        and c7_api_esc_dec
        and c8_api_esc_prio
        and c9_direct_match
    )

    if not passed:
        all_passed = False

    status = "PASS" if passed else "FAIL"
    results_table.append((q, api_intent, exp_intent, api_dec, api_trig, status))

    print(f"[{i:02d}] {status} | Query: \"{q}\"")
    print(f"     Actual:   Intent={api_intent!r}, Decision={api_dec!r}, Triggered={api_trig}, Priority={api_prio!r}")
    if not passed:
        print(f"     Expected: Intent={exp_intent!r}, Decision={exp_dec!r}, Triggered={exp_trig}, Priority={exp_prio!r}")
        print(f"     Checks:   Ans={c1_answer}, Intent={c2_intent}, Dec={c3_dec}, Trig={c4_trig}, Prio={c5_prio}, ApiEsc={c6_api_esc_intent and c7_api_esc_dec and c8_api_esc_prio}, DirectMatch={c9_direct_match}")

print("\n====================================================== SUMMARY TABLE ======================================================")
print(f"{'Query':<55} | {'Final Intent':<38} | {'Escalation':<18} | {'Triggered':<10} | {'Status'}")
print("-" * 140)
for q, intent, exp_intent, dec, trig, status in results_table:
    print(f"{q:<55} | {intent:<38} | {dec:<18} | {str(trig):<10} | {status}")
print("===========================================================================================================================")
print(f"ALL 13 API TEST CASES PASSED: {all_passed}")

if not all_passed:
    sys.exit(1)
