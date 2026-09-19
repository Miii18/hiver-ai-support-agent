"""Simple test for greeting handler without FAISS dependency."""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# Import only the greeting handler (no FAISS dependencies)
from src.chatbot.greeting_handler import GreetingHandler

def test_greetings():
    """Test greeting detection and responses."""
    test_cases = [
        ("Hello", "greeting"),
        ("Hi there", "greeting"),
        ("Hey!", "greeting"),
        ("Good morning", "greeting"),
        ("Good afternoon", "greeting"),
        ("Good evening", "greeting"),
        ("Thanks", "thank_you"),
        ("Thank you so much", "thank_you"),
        ("Bye", "goodbye"),
        ("Goodbye", "goodbye"),
        ("Where is my order?", "support"),
    ]

    print("=" * 70)
    print("GREETING HANDLER TESTS")
    print("=" * 70)
    print()

    passed = 0
    failed = 0

    for query, expected_type in test_cases:
        response = GreetingHandler.get_greeting_response(query)
        is_greeting = response is not None
        expected_greeting = expected_type != "support"

        if is_greeting == expected_greeting:
            status = "PASS"
            passed += 1
        else:
            status = "FAIL"
            failed += 1

        result_type = "Greeting" if response else "Support"
        print(f"[{status}] {query:30s} -> {result_type:10s}")

        if response:
            print(f"      Intent: {response['intent_label']}, Confidence: {response['confidence']}")
            print(f"      Answer: {response['answer'][:50]}...")
        print()

    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)
    print()
    print("RESPONSE STRUCTURE TEST")
    print("=" * 70)
    response = GreetingHandler.get_greeting_response("Hi")
    print(f"✓ answer: {response['answer']}")
    print(f"✓ intent_label: {response['intent_label']}")
    print(f"✓ intent_category: {response['intent_category']}")
    print(f"✓ confidence: {response['confidence']}")
    print(f"✓ is_greeting: {response['is_greeting']}")
    print(f"✓ context: {response['context']}")
    print()

if __name__ == "__main__":
    test_greetings()
