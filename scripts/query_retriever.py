from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.retrieval.retriever import retrieve


def main() -> int:
    print('Hiver retrieval demo. Type "exit" to quit.')
    while True:
        query = input('Customer support query: ').strip()
        if query.lower() in {'exit', 'quit'}:
            print('Goodbye.')
            return 0
        if not query:
            print('Please enter a query.')
            continue
        results = retrieve(query, top_k=5)
        if results.empty:
            print('No results found for that query.')
            continue

        print('\nTop 5 retrieved conversations:')
        for idx, row in results.iterrows():
            print(f"{idx + 1}. {row['intent_label']} | score={float(row['similarity_score']):.4f} | lang={row.get('language', 'unknown')}")
            print(f"   Query: {str(row['customer_query'])[:180]}")
            print(f"   Response: {str(row['amazon_response'])[:180]}")
            print(f"   Conversation ID: {row['conversation_id']}")
        print()


if __name__ == '__main__':
    sys.exit(main())
