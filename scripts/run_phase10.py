#!/usr/bin/env python
"""Phase 10 Hiver Assignment - Final Validation Script."""
import json
from pathlib import Path


def validate_phase10():
    """Validate all Phase 10 deliverables."""
    print("\n" + "=" * 80)
    print("PHASE 10 HIVER ASSIGNMENT VALIDATION")
    print("=" * 80 + "\n")

    artifacts = [
        # Part 1: Escalation Decision Engine
        ("src/escalation/__init__.py", "Escalation Module"),
        ("src/escalation/escalation_engine.py", "Escalation Engine"),
        ("src/escalation/escalation_rules.py", "Escalation Rules"),

        # Part 2: Golden Evaluation Dataset
        ("evaluation/golden_dataset/golden_dataset.json", "Golden Dataset (JSON)"),
        ("evaluation/golden_dataset/golden_dataset.csv", "Golden Dataset (CSV)"),

        # Part 3: Evaluation Harness
        ("evaluation/results/metrics.json", "Evaluation Metrics"),

        # Part 4: Baseline Comparison
        ("evaluation/baselines/baseline_comparison.json", "Baseline Comparison"),

        # Part 5: LLM-as-Judge Evaluation
        ("evaluation/judge/judge_results.json", "Judge Results"),

        # Part 7: Failure Analysis
        ("evaluation/failure_analysis/failure_cases.md", "Failure Analysis"),

        # Part 9: Decision Log
        ("docs/decision_log.md", "Decision Log"),
    ]

    results = []
    for artifact_path, description in artifacts:
        exists = Path(artifact_path).exists()
        status = "[PASS]" if exists else "[FAIL]"
        results.append((status, description, artifact_path, exists))
        print(f"{status} {description:40s} -> {artifact_path}")

    print("\n" + "=" * 80)

    all_passed = all(exists for _, _, _, exists in results)
    passed_count = sum(1 for _, _, _, exists in results if exists)
    total_count = len(results)

    print(f"Validation Results: {passed_count}/{total_count} artifacts found")
    print("=" * 80 + "\n")

    if all_passed:
        print("PHASE 10 HIVER ASSIGNMENT COMPLETED SUCCESSFULLY")
        return 0
    else:
        print("PHASE 10 VALIDATION INCOMPLETE - Some artifacts missing")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(validate_phase10())
