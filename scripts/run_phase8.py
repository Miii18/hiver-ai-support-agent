from __future__ import annotations

"""Run Phase 8 validation: starts the FastAPI app in test client and validates endpoints.

Prints a PASS/FAIL table and exact completion message on success.
"""
from pathlib import Path
import json
import sys
import logging

from fastapi.testclient import TestClient

# ensure project root is on sys.path before importing from src
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.api.app import app

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def run_checks() -> dict:
    client = TestClient(app)
    results = {}

    # health
    r = client.get('/health')
    results['health'] = r.status_code == 200 and r.json().get('status') == 'healthy'

    # intents
    r = client.get('/intents')
    results['intents'] = r.status_code == 200 and 'intents' in r.json()

    # chat
    r = client.post('/chat', json={'query': 'Where is my order?', 'top_k': 3})
    results['chat'] = r.status_code == 200 and 'answer' in r.json()

    # reset
    r = client.post('/reset')
    results['reset'] = r.status_code == 200 and r.json().get('status') == 'memory_reset'

    return results


def main():
    results = run_checks()
    # print table
    print('\nPhase 8 API validation results:')
    print('------------------------------')
    for k, v in results.items():
        print(f'{k:10s}:', 'PASS' if v else 'FAIL')

    if all(results.values()):
        print('\n# ======================================================')
        print('PHASE 8 COMPLETED SUCCESSFULLY')
        print('Include PASS / FAIL table.')
        sys.exit(0)
    else:
        print('\nPHASE 8 VALIDATION FAILED')
        sys.exit(2)


if __name__ == '__main__':
    main()

import json
import time
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run() -> int:
    start = time.time()
    print('\n# ======================================================')
    print('Running Phase 8 API validation...')
    # Run pytest for API tests
    rc = pytest.main(['-q', 'tests/test_phase8_api.py'])
    elapsed = time.time() - start
    print('\nValidation run complete.')
    print(f'Execution time: {elapsed:.2f} seconds')
    if rc == 0:
        print('# ====================================================== PHASE 8 COMPLETED SUCCESSFULLY')
        return 0
    print('# ====================================================== PHASE 8 FAILED')
    return rc


if __name__ == '__main__':
    sys.exit(run())
