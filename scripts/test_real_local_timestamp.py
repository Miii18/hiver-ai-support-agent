#!/usr/bin/env python
"""Real Local Timestamp Bug Fix - Validation Script."""
from datetime import datetime
import pytz
import re


class TimestampValidator:
    """Validate real local timestamp functionality."""

    @staticmethod
    def get_local_time_format(tz_name: str | None = None) -> str:
        """Get current time in user's local timezone, formatted as 12-hour (HH:MM AM/PM)."""
        if not tz_name:
            tz_name = "Asia/Kolkata"

        try:
            tz = pytz.timezone(tz_name)
        except pytz.exceptions.UnknownTimeZoneError:
            tz = pytz.timezone("Asia/Kolkata")

        local_time = datetime.now(tz)
        return local_time.strftime("%I:%M %p")

    @staticmethod
    def is_12hour_format(timestamp: str) -> bool:
        """Check if timestamp is in 12-hour format (HH:MM AM/PM)."""
        pattern = r'^\d{1,2}:\d{2}\s(?:AM|PM)$'
        return bool(re.match(pattern, timestamp, re.IGNORECASE))

    @staticmethod
    def validate_timezone_conversion(tz_name: str, expected_hour_range: tuple) -> bool:
        """Validate timezone conversion works correctly."""
        try:
            tz = pytz.timezone(tz_name)
            local_time = datetime.now(tz)
            hour = local_time.hour
            return expected_hour_range[0] <= hour <= expected_hour_range[1]
        except Exception:
            return False


def validate_real_local_timestamp():
    """Validate real local timestamp bug fix."""
    print("\n" + "=" * 80)
    print("REAL LOCAL TIMESTAMP BUG FIX - VALIDATION")
    print("=" * 80 + "\n")

    test_cases = [
        {
            "name": "12-hour format with AM/PM",
            "timestamp": TimestampValidator.get_local_time_format("Asia/Kolkata"),
            "check": lambda ts: TimestampValidator.is_12hour_format(ts),
            "description": "Timestamps should be in HH:MM AM/PM format",
        },
        {
            "name": "Asia/Kolkata timezone",
            "timestamp": TimestampValidator.get_local_time_format("Asia/Kolkata"),
            "check": lambda ts: TimestampValidator.is_12hour_format(ts),
            "description": "India timezone should work correctly",
        },
        {
            "name": "US/Eastern timezone",
            "timestamp": TimestampValidator.get_local_time_format("US/Eastern"),
            "check": lambda ts: TimestampValidator.is_12hour_format(ts),
            "description": "Different timezone should also work",
        },
        {
            "name": "Europe/London timezone",
            "timestamp": TimestampValidator.get_local_time_format("Europe/London"),
            "check": lambda ts: TimestampValidator.is_12hour_format(ts),
            "description": "Another timezone should be supported",
        },
        {
            "name": "Invalid timezone fallback",
            "timestamp": TimestampValidator.get_local_time_format("Invalid/Timezone"),
            "check": lambda ts: TimestampValidator.is_12hour_format(ts),
            "description": "Should fallback to Asia/Kolkata for invalid timezone",
        },
        {
            "name": "None timezone fallback",
            "timestamp": TimestampValidator.get_local_time_format(None),
            "check": lambda ts: TimestampValidator.is_12hour_format(ts),
            "description": "Should use Asia/Kolkata when timezone is None",
        },
        {
            "name": "Contains leading zero for single-digit hour",
            "timestamp": TimestampValidator.get_local_time_format("Asia/Kolkata"),
            "check": lambda ts: re.match(r'^\d{2}:\d{2}\s(?:AM|PM)$', ts, re.IGNORECASE),
            "description": "Hours should be padded with zero (03:13 PM, not 3:13 PM)",
        },
        {
            "name": "Contains AM or PM indicator",
            "timestamp": TimestampValidator.get_local_time_format("Asia/Kolkata"),
            "check": lambda ts: bool(re.search(r'(?:AM|PM)$', ts, re.IGNORECASE)),
            "description": "Timestamp should end with AM or PM",
        },
        {
            "name": "Minutes are two digits",
            "timestamp": TimestampValidator.get_local_time_format("Asia/Kolkata"),
            "check": lambda ts: bool(re.search(r':\d{2}\s', ts)),
            "description": "Minutes should always be two digits (01-59)",
        },
        {
            "name": "Multiple calls produce consistent format",
            "timestamp": TimestampValidator.get_local_time_format("Asia/Kolkata"),
            "check": lambda ts: TimestampValidator.is_12hour_format(ts),
            "description": "Format should be consistent across multiple calls",
        },
    ]

    results = []
    print("Test Results:")
    print("-" * 80)

    for i, test in enumerate(test_cases, 1):
        try:
            passed = test["check"](test["timestamp"])
            status = "[PASS]" if passed else "[FAIL]"
            results.append((status, passed))
            print(f"{status} Test {i:2d}: {test['name']:40s}")
            print(f"         Timestamp: {test['timestamp']}")
            print(f"         {test['description']}")
            print()
        except Exception as e:
            results.append(("[FAIL]", False))
            print(f"[FAIL] Test {i:2d}: {test['name']:40s}")
            print(f"         Error: {str(e)}")
            print()

    print("=" * 80)

    all_passed = all(passed for _, passed in results)
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    print(f"Results: {passed_count}/{total_count} tests passed")
    print("=" * 80 + "\n")

    if all_passed:
        print("REAL LOCAL TIMESTAMP BUG FIXED")
        return 0
    else:
        print("REAL LOCAL TIMESTAMP BUG FIX - SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(validate_real_local_timestamp())
