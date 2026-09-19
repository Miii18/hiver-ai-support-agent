#!/usr/bin/env python
"""Phase 9 Polish Validation - Test improved intent classification and UI display."""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# Test queries
TEST_QUERIES = [
    ("Hello", "Greeting", 1.0),
    ("Thanks", "Greeting", 1.0),
    ("Bye", "Greeting", 1.0),
    ("My Amazon package has not been delivered.", "Delivery", 0.9),
    ("I want a refund for my order.", "Returns & Refunds", 0.9),
    ("Cancel my Prime membership.", "Prime Membership", 0.9),
    ("I forgot my Amazon password.", "Login & Authentication", 0.9),
    ("Coupon code is not working.", "Promotions & Coupons", 0.9),
    ("Amazon app crashes every time I open it.", "Technical Issue", 0.9),
]


def test_improved_classifier():
    """Test improved intent classifier with keyword matching."""
    try:
        from src.chatbot.improved_intent_classifier import ImprovedIntentClassifier
    except ImportError:
        print("ERROR: Cannot import ImprovedIntentClassifier")
        return False

    classifier = ImprovedIntentClassifier()
    all_passed = True

    print("\n" + "=" * 80)
    print("TESTING IMPROVED INTENT CLASSIFIER")
    print("=" * 80)

    for query, expected_intent, expected_confidence in TEST_QUERIES:
        result = classifier.classify_by_keywords(query)

        if result is None:
            print("[FAIL] {0:50s} -> No match".format(query))
            all_passed = False
            continue

        intent, confidence = result
        passed = intent == expected_intent and confidence >= expected_confidence - 0.01

        status = "PASS" if passed else "FAIL"
        print("[{0}] {1:50s}".format(status, query))
        print("      Intent: {0:30s} (expected: {1})".format(intent, expected_intent))
        print("      Confidence: {0:.0%} (expected: >= {1:.0%})".format(confidence, expected_confidence))

        if not passed:
            all_passed = False

    return all_passed


def test_display_names():
    """Test display name mapping."""
    try:
        from src.chatbot.improved_intent_classifier import ImprovedIntentClassifier
    except ImportError:
        print("ERROR: Cannot import ImprovedIntentClassifier")
        return False

    classifier = ImprovedIntentClassifier()
    all_passed = True

    print("\n" + "=" * 80)
    print("TESTING DISPLAY NAME MAPPING")
    print("=" * 80)

    test_mappings = [
        ("Customer Amazon Order", "Orders"),
        ("Que Amazon Customer", "Returns & Refunds"),
        ("Amazon Customer Tn", "Prime Membership"),
        ("Amazon Customer Contest", "Promotions & Coupons"),
        ("Amazon Vous Customer", "Delivery"),
        ("Customer Amazon Die", "Login & Authentication"),
        ("Customer Amazon Que", "Technical Issue"),
        ("Other", "Other Support"),
        ("Greeting", "Greeting"),
    ]

    for internal, expected_display in test_mappings:
        result = classifier.get_display_name(internal)
        passed = result == expected_display

        status = "PASS" if passed else "FAIL"
        print("[{0}] {1:30s} -> {2:25s} (expected: {3})".format(status, internal, result, expected_display))

        if not passed:
            all_passed = False

    return all_passed


def test_confidence_colors():
    """Test confidence color coding."""
    try:
        from src.chatbot.improved_intent_classifier import ImprovedIntentClassifier
    except ImportError:
        print("ERROR: Cannot import ImprovedIntentClassifier")
        return False

    classifier = ImprovedIntentClassifier()
    all_passed = True

    print("\n" + "=" * 80)
    print("TESTING CONFIDENCE COLOR CODING")
    print("=" * 80)

    test_cases = [
        (0.95, "green", "High confidence"),
        (0.80, "green", "Minimum green threshold"),
        (0.75, "yellow", "Mid-range confidence"),
        (0.60, "yellow", "Minimum yellow threshold"),
        (0.50, "red", "Low confidence"),
        (0.30, "red", "Very low confidence"),
    ]

    for confidence, expected_color, desc in test_cases:
        result = classifier.get_confidence_color(confidence)
        passed = result == expected_color

        status = "PASS" if passed else "FAIL"
        print("[{0}] {1:.0%} -> {2:6s} (expected: {3:6s}) - {4}".format(status, confidence, result, expected_color, desc))

        if not passed:
            all_passed = False

    return all_passed


def test_response_templates():
    """Test response template builder."""
    try:
        from src.chatbot.response_template_builder import ResponseTemplateBuilder
    except ImportError:
        print("ERROR: Cannot import ResponseTemplateBuilder")
        return False

    all_passed = True

    print("\n" + "=" * 80)
    print("TESTING RESPONSE TEMPLATE BUILDER")
    print("=" * 80)

    test_intents = [
        "Returns & Refunds",
        "Delivery",
        "Orders",
        "Prime Membership",
        "Login & Authentication",
        "Promotions & Coupons",
        "Technical Issue",
    ]

    for intent in test_intents:
        response = ResponseTemplateBuilder.build_response(
            intent=intent,
            base_answer="Sample answer for {0}".format(intent),
            context=[],
        )

        # Check that response contains template structure
        has_structure = ("Regarding" in response or "regarding" in response.lower()) or ("can do" in response.lower())

        status = "PASS" if has_structure else "FAIL"
        print("[{0}] {1:30s} - Template applied correctly".format(status, intent))

        if not has_structure:
            all_passed = False

    return all_passed


def main():
    """Run all validation tests."""
    print("\n")
    print("=" * 80)
    print("PHASE 9 POLISH VALIDATION")
    print("=" * 80)

    results = []

    # Run all tests
    results.append(("Intent Classifier", test_improved_classifier()))
    results.append(("Display Names", test_display_names()))
    results.append(("Confidence Colors", test_confidence_colors()))
    results.append(("Response Templates", test_response_templates()))

    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    all_passed = True
    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        print("[{0}] {1}".format(status, test_name))
        if not passed:
            all_passed = False

    print("=" * 80)

    if all_passed:
        print("\nPHASE 9 POLISH VALIDATION PASSED")
        print()
        return 0
    else:
        print("\nPHASE 9 POLISH VALIDATION FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
