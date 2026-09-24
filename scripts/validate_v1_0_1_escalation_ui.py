#!/usr/bin/env python
"""VERSION 1.0.1 Escalation Banner UI validation."""
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


def load_module_direct(rel_path, mod_name):
    abs_path = PROJECT_ROOT / rel_path
    spec = importlib.util.spec_from_file_location(mod_name, abs_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


print()
print('=' * 64)
print('VERSION 1.0.1 — ESCALATION BANNER UI VALIDATION')
print('=' * 64)

# ── 1: ResponseTemplateBuilder classifier ─────────────────────
print('\n1. ResponseTemplateBuilder.classify_escalation_type():')
rtb = load_module_direct('src/chatbot/response_template_builder.py', 'response_template_builder')
RTB = rtb.ResponseTemplateBuilder

check('classify_escalation_type classmethod exists',
      hasattr(RTB, 'classify_escalation_type'))
check('BANNER_CONFIG dict present',
      hasattr(RTB, 'BANNER_CONFIG'))
check('BANNER_CONFIG has security key', 'security' in RTB.BANNER_CONFIG)
check('BANNER_CONFIG has billing key', 'billing' in RTB.BANNER_CONFIG)
check('BANNER_CONFIG has refund key', 'refund' in RTB.BANNER_CONFIG)
check('BANNER_CONFIG has damaged key', 'damaged' in RTB.BANNER_CONFIG)

# ── 2: Classify the four test queries ─────────────────────────
print('\n2. Correct banner type for each test query:')

q1_type, q1_reason = RTB.classify_escalation_type(
    query="Account hacked", intent="Login & Authentication", raw_reason="Critical issue detected: account.*hacked")
check('"Account hacked" → security type', q1_type == 'security',
      f'got {q1_type!r}')
check('"Account hacked" reason is human-friendly (no regex)',
      'account.*hacked' not in q1_reason and 'compromise' in q1_reason.lower() or 'account' in q1_reason.lower(),
      f'got {q1_reason!r}')

q2_type, q2_reason = RTB.classify_escalation_type(
    query="Charged twice", intent="Billing", raw_reason="Critical issue detected: charge.*twice")
check('"Charged twice" → billing type', q2_type == 'billing',
      f'got {q2_type!r}')
check('"Charged twice" reason is human-friendly (no regex)',
      'charge.*twice' not in q2_reason,
      f'got {q2_reason!r}')

q3_type, q3_reason = RTB.classify_escalation_type(
    query="Refund pending 45 days", intent="Returns & Refunds", raw_reason="Critical issue: refund.*pending.*long")
check('"Refund pending 45 days" → refund type', q3_type == 'refund',
      f'got {q3_type!r}')
check('"Refund pending 45 days" reason mentions refund',
      'refund' in q3_reason.lower(),
      f'got {q3_reason!r}')

q4_type, q4_reason = RTB.classify_escalation_type(
    query="Received torn packet", intent="Delivery", raw_reason="")
check('"Received torn packet" → damaged type', q4_type == 'damaged',
      f'got {q4_type!r}')
check('"Received torn packet" reason mentions damage',
      'damage' in q4_reason.lower() or 'product' in q4_reason.lower(),
      f'got {q4_reason!r}')

# ── 3: BANNER_CONFIG structure per type ───────────────────────
print('\n3. BANNER_CONFIG structure:')
required_keys = {'color', 'border', 'bg_gradient', 'badge_bg', 'icon', 'label', 'next_steps'}
for btype in ('security', 'billing', 'refund', 'damaged'):
    cfg = RTB.BANNER_CONFIG[btype]
    check(f'{btype} config has all required keys',
          required_keys.issubset(set(cfg.keys())),
          f'missing {required_keys - set(cfg.keys())}')
    check(f'{btype} has 3–4 next_steps',
          3 <= len(cfg['next_steps']) <= 4,
          f'got {len(cfg["next_steps"])} steps')

# ── 4: correct colors ─────────────────────────────────────────
print('\n4. Banner color check:')
check('Security uses red (#dc2626)', '#dc2626' in RTB.BANNER_CONFIG['security']['color'])
check('Billing uses orange (#ea580c)', '#ea580c' in RTB.BANNER_CONFIG['billing']['color'])
check('Refund uses blue (#2563eb)', '#2563eb' in RTB.BANNER_CONFIG['refund']['color'])
check('Damaged uses amber (#d97706)', '#d97706' in RTB.BANNER_CONFIG['damaged']['color'])

# ── 5: Streamlit UI banner code ───────────────────────────────
print('\n5. Streamlit UI — premium banner HTML:')
ui_src = open(PROJECT_ROOT / 'src/ui/streamlit_app.py').read()

check('ResponseTemplateBuilder imported in streamlit_app',
      'ResponseTemplateBuilder' in ui_src)
check('classify_escalation_type called in streamlit_app',
      'classify_escalation_type' in ui_src)
check('BANNER_CONFIG referenced in streamlit_app',
      'BANNER_CONFIG' in ui_src)
check('No raw enum text in banner (EscalationPriority.)',
      'EscalationPriority.' not in ui_src)
check('No old plain red card hex (#b91c1c)',
      '#b91c1c' not in ui_src)
check('Gradient background present', 'bg_gradient' in ui_src)
check('Priority badge present', 'Priority:' in ui_src)
check('Next Steps checklist present', 'Next Steps' in ui_src)
check('Routed to human support specialist footer present',
      'routed to a human support specialist' in ui_src)
check('Priority label still uses .capitalize()',
      'capitalize' in ui_src)

# ── Summary ───────────────────────────────────────────────────
print()
print('=' * 64)
total = PASS_COUNT + FAIL_COUNT
print(f'Results: {PASS_COUNT}/{total} checks passed')
print('=' * 64)

if FAIL_COUNT == 0:
    print()
    print('VERSION 1.0.1 ESCALATION UI COMPLETED')
else:
    print()
    print(f'VALIDATION FAILED — {FAIL_COUNT} check(s) failed')
    sys.exit(1)
