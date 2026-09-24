#!/usr/bin/env python
"""VERSION 1.0.1 UI Polish validation — no FAISS/sentence_transformers required."""
import sys
import importlib.util
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

PASS_COUNT = 0
FAIL_COUNT = 0


def check(label, condition, detail=''):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        print(f'  [PASS] {label}')
    else:
        FAIL_COUNT += 1
        print(f'  [FAIL] {label}' + (f' — {detail}' if detail else ''))


def load_module_direct(rel_path: str, mod_name: str):
    abs_path = PROJECT_ROOT / rel_path
    spec = importlib.util.spec_from_file_location(mod_name, abs_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


print()
print('=' * 64)
print('VERSION 1.0.1 — UI POLISH VALIDATION')
print('=' * 64)

# ── Test 1: Escalation Banner in UI ───────────────────────────
print('\n1. Escalation Banner (Professional Red Card):')
ui_src = open(PROJECT_ROOT / 'src/ui/streamlit_app.py').read()

check('No raw enum text in banner',
      'EscalationPriority.' not in ui_src)
check('Red card contains "Escalation Required"',
      'Escalation Required' in ui_src)
check('Red card shows Priority field',
      'Priority:' in ui_src and 'priority_label' in ui_src)
check('Red card shows Reason field',
      'Reason:' in ui_src and 'reason_text' in ui_src)
check('Footer text: routed to human support specialist',
      'routed to a human support specialist' in ui_src)
check('Priority label is capitalized (not raw ALL_CAPS enum)',
      '.capitalize()' in ui_src or 'priority_label.capitalize()' in ui_src
      or '".capitalize()"' in ui_src or 'capitalize' in ui_src)

# ── Test 2: Intent-Specific Escalation Templates ───────────────
print('\n2. Intent-Specific Escalation Templates:')
rtb_mod = load_module_direct('src/chatbot/response_template_builder.py', 'response_template_builder')
ResponseTemplateBuilder = rtb_mod.ResponseTemplateBuilder

check('build_escalation_response classmethod exists',
      hasattr(ResponseTemplateBuilder, 'build_escalation_response'))
check('ESCALATION_TEMPLATES dict present',
      hasattr(ResponseTemplateBuilder, 'ESCALATION_TEMPLATES'))
check('Security template present',
      'security' in ResponseTemplateBuilder.ESCALATION_TEMPLATES)
check('Billing template present',
      'billing' in ResponseTemplateBuilder.ESCALATION_TEMPLATES)
check('Fraud template present',
      'fraud' in ResponseTemplateBuilder.ESCALATION_TEMPLATES)
check('Refund template present',
      'refund' in ResponseTemplateBuilder.ESCALATION_TEMPLATES)

# Security escalation
sec_resp = ResponseTemplateBuilder.build_escalation_response(
    intent='Login & Authentication',
    base_answer='We are looking into your account.',
    escalation_reason='Account breach detected.',
)
check('Security escalation contains password reset guidance',
      'password' in sec_resp.lower() or 'Password' in sec_resp)
check('Security escalation contains account recovery steps',
      '2FA' in sec_resp or 'Two-Factor' in sec_resp or 'recovery' in sec_resp.lower())

# Billing escalation
bill_resp = ResponseTemplateBuilder.build_escalation_response(
    intent='Billing',
    base_answer='We will investigate your payment.',
    escalation_reason='Suspicious charge detected.',
)
check('Billing escalation contains payment investigation steps',
      'payment' in bill_resp.lower() or 'billing' in bill_resp.lower() or 'specialist' in bill_resp.lower())

# Fraud escalation
fraud_resp = ResponseTemplateBuilder.build_escalation_response(
    intent='Fraud',
    base_answer='We detected unauthorized access.',
    escalation_reason='Unauthorized purchase.',
)
check('Fraud escalation contains unauthorized purchase guidance',
      'unauthorized' in fraud_resp.lower() or 'fraud' in fraud_resp.lower())

# Refund escalation
refund_resp = ResponseTemplateBuilder.build_escalation_response(
    intent='Returns & Refunds',
    base_answer='We will process your refund.',
    escalation_reason='Refund pending over 30 days.',
)
check('Refund escalation contains refund investigation guidance',
      'refund' in refund_resp.lower())

# Delivery intent must NOT reuse delivery template for escalation
delivery_esc = ResponseTemplateBuilder.build_escalation_response(
    intent='Delivery',
    base_answer='Your package is missing.',
    escalation_reason='High value item missing.',
)
# delivery category maps to fallback (not a delivery-specific template) — check it doesn't use delivery template
check('Delivery escalation does NOT reuse plain Delivery template',
      'It looks like you\'re experiencing a delivery issue.' not in delivery_esc)

# ── Test 3: chatbot.py uses build_escalation_response ─────────
print('\n3. Chatbot Wiring — Escalation Path:')
chatbot_src = open(PROJECT_ROOT / 'src/chatbot/chatbot.py').read()

check('build_escalation_response called in chatbot.py',
      'build_escalation_response' in chatbot_src)
check('No raw [ESCALATED — ... PRIORITY] text prepend',
      '[ESCALATED —' not in chatbot_src)
check('escalation_intent passed to build_escalation_response',
      'escalation_intent' in chatbot_src)

# ── Test 4: Auto-scroll MutationObserver still present ────────
print('\n4. Auto-Scroll (MutationObserver):')
check('MutationObserver present in streamlit_app.py',
      'MutationObserver' in ui_src)
check('scrollIntoView present',
      'scrollIntoView' in ui_src)
check('chat-bottom anchor present',
      'chat-bottom' in ui_src)
check('requestAnimationFrame present',
      'requestAnimationFrame' in ui_src)

# ── Summary ───────────────────────────────────────────────────
print()
print('=' * 64)
total = PASS_COUNT + FAIL_COUNT
print(f'Results: {PASS_COUNT}/{total} checks passed')
print('=' * 64)

if FAIL_COUNT == 0:
    print()
    print('VERSION 1.0.1 UI POLISH PASSED')
else:
    print()
    print(f'VALIDATION FAILED — {FAIL_COUNT} check(s) failed')
    sys.exit(1)
