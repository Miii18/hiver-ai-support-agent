from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.chatbot.chatbot import SupportChatbot


def run() -> int:
    start = time.time()
    chatbot = SupportChatbot(top_k=3)
    test_queries = [
        'where is my order?',
        'I need help with my package delivery',
        'my account is locked and I need access',
    ]
    responses = []
    for query in test_queries:
        response = chatbot.answer_query(query)
        responses.append(response)

    print('\n# ======================================================')
    print('PHASE 7 COMPLETED SUCCESSFULLY')
    print(f'Total queries processed: {len(responses)}')
    print(f'Average confidence: {sum(float(item["confidence"]) for item in responses) / max(len(responses), 1):.4f}')
    print(f'Execution time: {time.time() - start:.2f} seconds')
    print('# ====================================================== PHASE 7 COMPLETED SUCCESSFULLY')
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run the Phase 7 chatbot pipeline.')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    sys.exit(run())
