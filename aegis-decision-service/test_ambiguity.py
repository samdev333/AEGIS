#!/usr/bin/env python3
"""
Test script for A.E.G.I.S. ambiguity detection and validation.

Tests the updated prompt v2 with ambiguity-aware confidence scoring.

Usage:
    # Test with mocked watsonx responses
    MOCK_WATSONX=1 python test_ambiguity.py

    # Test with real watsonx.ai (requires credentials)
    python test_ambiguity.py
"""

import os
import sys

# Set MOCK_WATSONX=1 by default for testing
if "MOCK_WATSONX" not in os.environ:
    os.environ["MOCK_WATSONX"] = "1"

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from aegis_service.watsonx_client import WatsonxClient


def test_case(name: str, incident_text: str, expected_conf_max: int, expected_actions: list) -> bool:
    """
    Run a single test case.

    Args:
        name: Test case name
        incident_text: Incident description
        expected_conf_max: Maximum expected confidence score
        expected_actions: List of acceptable actions

    Returns:
        True if test passes, False otherwise
    """
    print(f"\n{'='*70}")
    print(f"TEST: {name}")
    print(f"{'='*70}")
    print(f"Input: {incident_text}")
    print()

    client = WatsonxClient()
    decision = client.get_decision(
        incident_text=incident_text,
        category="unknown",
        reporter_role="SRE",
        runbook_context=""
    )

    print(f"Analysis: {decision.analysis}")
    print(f"Action: {decision.recommended_action}")
    print(f"Confidence: {decision.confidence_score}")
    print(f"Explanation: {decision.explanation}")
    print()

    # Check confidence
    conf_ok = decision.confidence_score <= expected_conf_max
    print(f"[OK] Confidence <= {expected_conf_max}: {conf_ok} (got {decision.confidence_score})")

    # Check action
    action_ok = decision.recommended_action in expected_actions
    print(f"[OK] Action in {expected_actions}: {action_ok} (got '{decision.recommended_action}')")

    # Check no auto-resolution language if confidence < 90
    if decision.confidence_score < 90:
        auto_resolve_terms = ["auto-resolved", "resolved automatically", "will be resolved"]
        has_auto_resolve = any(term in decision.explanation.lower() for term in auto_resolve_terms)
        no_auto_resolve_ok = not has_auto_resolve
        print(f"[OK] No auto-resolution language: {no_auto_resolve_ok}")
    else:
        no_auto_resolve_ok = True
        print(f"[OK] No auto-resolution check: N/A (confidence >= 90)")

    passed = conf_ok and action_ok and no_auto_resolve_ok
    print()
    print(f"Result: {'PASS [OK]' if passed else 'FAIL [X]'}")

    return passed


def main():
    """Run all test cases"""
    print("A.E.G.I.S. Ambiguity Detection Tests")
    print(f"Mock mode: {os.environ.get('MOCK_WATSONX', '0')}")
    print()

    results = []

    # Test 1: Ambiguous incident (latency high but metrics normal)
    results.append(test_case(
        name="Ambiguous Incident - Conflicting Signals",
        incident_text="Database latency is high but system metrics look normal.",
        expected_conf_max=60,
        expected_actions=["escalate_to_human", "run_diagnostics"]
    ))

    # Test 2: Clear disk space issue
    results.append(test_case(
        name="Clear Issue - Disk Space",
        incident_text="Disk space is at 99% on Server-DB-01; /var/log growing rapidly.",
        expected_conf_max=100,  # Allow any score, but should be high
        expected_actions=["clear_logs", "run_diagnostics"]  # Either is acceptable
    ))

    # Test 3: Intermittent issue with no clear pattern
    results.append(test_case(
        name="Ambiguous Incident - No Clear Pattern",
        incident_text="Intermittent authentication failures reported. No clear pattern in logs. May be related to deployment.",
        expected_conf_max=60,
        expected_actions=["escalate_to_human", "run_diagnostics"]
    ))

    # Test 4: Clear latency issue with identified cause
    results.append(test_case(
        name="Clear Issue - Database Slow Query",
        incident_text="Database latency spiked to 5000ms. Slow query log shows unoptimized SELECT on orders table. CPU at 95%.",
        expected_conf_max=100,  # Allow any score
        expected_actions=["run_diagnostics", "escalate_to_human"]  # Depends on confidence
    ))

    # Test 5: Multiple possible causes
    results.append(test_case(
        name="Ambiguous Incident - Multiple Possible Causes",
        incident_text="Application crashed. Could be memory leak, could be database timeout, unclear from logs.",
        expected_conf_max=60,
        expected_actions=["escalate_to_human", "run_diagnostics"]
    ))

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    print()

    if passed == total:
        print("[OK] All tests passed!")
        return 0
    else:
        print("[X] Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
