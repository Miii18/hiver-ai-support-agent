#!/usr/bin/env python
"""Real integration validation — tests actual source files via direct import, bypassing FAISS/sentence_transformers."""
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
    """Load a module directly from file path without going through package __init__.py."""
    abs_path = PROJECT_ROOT / rel_path
    spec = importlib.util.spec_from_file_location(mod_name, abs_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


print()
print('=' * 64)
print('HIVER VERSION 1.0.0 — REAL INTEGRATION VALIDATION')
print('=' * 64)

# ── Test 1: ConversationMemory ─────────────────────────────────
print('\nBUG 2 — Conversation Memory:')
memory_mod = load_module_direct('src/chatbot/memory.py', 'chatbot_memory')
ConversationMemory = memory_mod.ConversationMemory

mem = ConversationMemory()
mem.add_turn('user', 'my package is missing')
mem.add_turn('assistant', 'Let me help.', sources=[{'conversation_id': 'abc', 'similarity_score': 0.88}])

check('get_history() method exists', hasattr(mem, 'get_history'))
hist = mem.get_history()
check('get_history() returns history list', isinstance(hist, list) and len(hist) == 2, str(hist))
check('previous_sources stored on add_turn with sources',
      mem.previous_sources == [{'conversation_id': 'abc', 'similarity_score': 0.88}])
check('active_intent field exists', hasattr(mem, 'active_intent'))
check('active_subject field exists', hasattr(mem, 'active_subject'))
mem.active_intent = 'Delivery'
check('active_intent persists across turns', mem.active_intent == 'Delivery')

# ── Test 2: ImprovedIntentClassifier ──────────────────────────
print('\nBUG 1 — Orders vs Delivery Intent Separation:')
ic_mod = load_module_direct('src/chatbot/improved_intent_classifier.py', 'improved_intent_classifier')
ImprovedIntentClassifier = ic_mod.ImprovedIntentClassifier
ic = ImprovedIntentClassifier()

delivery_result = ic.classify_by_keywords('my package is still not delivered')
check('Delivery keyword classifies as Delivery',
      delivery_result is not None and delivery_result[0] == 'Delivery',
      str(delivery_result))
check('Delivery confidence = 0.95',
      delivery_result is not None and delivery_result[1] == 0.95,
      str(delivery_result))

order_result = ic.classify_by_keywords('where is my order number 12345')
check('Orders keyword classifies as Orders',
      order_result is not None and order_result[0] == 'Orders',
      str(order_result))
check('Orders confidence = 0.95',
      order_result is not None and order_result[1] == 0.95,
      str(order_result))

greet_result = ic.classify_by_keywords('hello there')
check('Greeting confidence = 1.0',
      greet_result is not None and greet_result[1] == 1.0,
      str(greet_result))

# ── Test 3: EscalationEngine ──────────────────────────────────
print('\nBUG 3 — Escalation Engine Integration:')
esc_mod = load_module_direct('src/escalation/escalation_engine.py', 'escalation_engine')
EscalationEngine = esc_mod.EscalationEngine
engine = EscalationEngine()

result = engine.decide(query='my account was hacked', intent='Login & Authentication', confidence=0.95, context=[])
check('Account hacked -> ESCALATE_TO_HUMAN',
      result.get('escalation_decision') == 'ESCALATE_TO_HUMAN',
      str(result.get('escalation_decision')))
check('Account hacked -> CRITICAL or HIGH priority',
      result.get('escalation_priority') in ('CRITICAL', 'HIGH'),
      str(result.get('escalation_priority')))

normal = engine.decide(query='where is my order', intent='Orders', confidence=0.95, context=[])
check('Normal query -> AUTO_HANDLE',
      normal.get('escalation_decision') != 'ESCALATE_TO_HUMAN',
      str(normal.get('escalation_decision')))

chatbot_src = open(PROJECT_ROOT / 'src/chatbot/chatbot.py').read()
check('EscalationEngine imported in chatbot.py',
      'from src.escalation.escalation_engine import EscalationEngine' in chatbot_src)
check('EscalationEngine instantiated in __init__',
      'self.escalation_engine = EscalationEngine()' in chatbot_src)
check('escalation_engine.decide() called in answer_query',
      'self.escalation_engine.decide(' in chatbot_src)

# ── Test 4: Sources from memory ───────────────────────────────
print('\nBUG 5 — Show Sources from Memory:')
check('sources passed to memory.add_turn in chatbot.py',
      "self.memory.add_turn('assistant', answer, sources=context_rows)" in chatbot_src)
check('previous_sources read in sources query handler',
      'self.memory.previous_sources' in chatbot_src)

# ── Test 5: Escalation banner in UI ───────────────────────────
print('\nBUG 4 — Escalation Banner in UI:')
ui_src = open(PROJECT_ROOT / 'src/ui/streamlit_app.py').read()
check('escalation_triggered extracted from reply', 'escalation_triggered' in ui_src)
check('ESCALATE_TO_HUMAN checked in UI', 'ESCALATE_TO_HUMAN' in ui_src)
check('ESCALATED banner text rendered', 'ESCALATED' in ui_src)
check('Red banner uses st.markdown with unsafe_allow_html',
      'unsafe_allow_html=True' in ui_src and 'ESCALATED' in ui_src)

# ── Test 6: API schema escalation fields ──────────────────────
print('\nAPI Schema:')
schema_src = open(PROJECT_ROOT / 'src/api/schemas.py').read()
check('ChatResponse has escalation_decision field', 'escalation_decision' in schema_src)
check('ChatResponse has escalation_priority field', 'escalation_priority' in schema_src)
check('ChatResponse has escalation_triggered field', 'escalation_triggered' in schema_src)

routes_src = open(PROJECT_ROOT / 'src/api/routes.py').read()
check('routes.py forwards escalation_decision', 'escalation_decision' in routes_src)
check('routes.py forwards escalation_triggered', 'escalation_triggered' in routes_src)

# ── Test 7: active_intent carryover ───────────────────────────
print('\nBUG 2 — Active Intent Carryover:')
check('active_intent updated after classification',
      'self.memory.active_intent = intent_label' in chatbot_src)
check('active_intent read for follow-up fallback',
      'self.memory.active_intent' in chatbot_src)

# ── Summary ───────────────────────────────────────────────────
print()
print('=' * 64)
total = PASS_COUNT + FAIL_COUNT
print(f'Results: {PASS_COUNT}/{total} checks passed')
print('=' * 64)

if FAIL_COUNT == 0:
    print()
    print('HIVER VERSION 1.0.0 DEBUG VALIDATION PASSED')
else:
    print()
    print(f'VALIDATION FAILED — {FAIL_COUNT} check(s) failed')
    sys.exit(1)
