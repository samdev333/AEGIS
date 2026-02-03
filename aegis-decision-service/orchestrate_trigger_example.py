#!/usr/bin/env python3
"""
Example: Trigger A.E.G.I.S. Decision Service via watsonx Orchestrate SDK

This script shows how to programmatically interact with your Orchestrate
instance to trigger the A.E.G.I.S. skill.

Use this pattern to integrate with ServiceNow or other systems.
"""

import os
from ibm_watsonx_orchestrate import Orchestrate

# Configuration
ORCHESTRATE_API_KEY = os.environ.get("ORCHESTRATE_API_KEY", "")
ORCHESTRATE_URL = os.environ.get("ORCHESTRATE_URL", "https://api.eu-gb.watson-orchestrate.cloud.ibm.com/instances/YOUR_INSTANCE_ID")

def trigger_aegis_analysis(incident_text: str, category: str = "unknown"):
    """
    Trigger A.E.G.I.S. decision service analysis via Orchestrate SDK.

    Args:
        incident_text: The incident description
        category: Incident category (latency, storage, auth, unknown)

    Returns:
        dict: Analysis result with confidence score and recommendation
    """

    # Initialize Orchestrate client
    client = Orchestrate(
        api_key=ORCHESTRATE_API_KEY,
        url=ORCHESTRATE_URL
    )

    # Trigger the A.E.G.I.S. skill
    # Note: Replace 'aegis_triage_agent' with your actual skill name
    result = client.run_skill(
        skill_name="aegis_triage_agent",
        inputs={
            "incident_text": incident_text,
            "category": category
        }
    )

    return result


def servicenow_integration_example():
    """
    Example: How to integrate with ServiceNow

    This function simulates receiving a ServiceNow incident
    and triggering A.E.G.I.S. analysis.
    """

    # Simulate ServiceNow incident data
    servicenow_incident = {
        "number": "INC0012345",
        "short_description": "Database latency is high but system metrics look normal",
        "description": "Users reporting slow response times. Database latency increased to 5000ms. CPU, memory, and disk metrics all within normal range.",
        "priority": "1-High",
        "category": "Database",
        "state": "New"
    }

    print("=" * 70)
    print("ServiceNow Incident Received")
    print("=" * 70)
    print(f"Incident: {servicenow_incident['number']}")
    print(f"Description: {servicenow_incident['short_description']}")
    print(f"Priority: {servicenow_incident['priority']}")
    print()

    # Combine short description and full description
    incident_text = f"{servicenow_incident['short_description']}. {servicenow_incident['description']}"

    # Map ServiceNow category to A.E.G.I.S. category
    category_mapping = {
        "Database": "latency",
        "Storage": "storage",
        "Authentication": "auth"
    }
    aegis_category = category_mapping.get(servicenow_incident['category'], "unknown")

    print("Triggering A.E.G.I.S. Analysis...")
    print()

    # Trigger analysis
    try:
        result = trigger_aegis_analysis(incident_text, aegis_category)

        print("=" * 70)
        print("A.E.G.I.S. Analysis Result")
        print("=" * 70)
        print(f"Analysis: {result.get('analysis')}")
        print(f"Confidence Score: {result.get('confidence_score')}%")
        print(f"Recommended Action: {result.get('recommended_action')}")
        print(f"Explanation: {result.get('explanation')}")
        print()

        # Decision logic based on confidence
        if result.get('confidence_score', 0) >= 80:
            print("🟢 HIGH CONFIDENCE - Routing to Auto-Execute Path")
            print(f"   → Action: {result.get('recommended_action')}")
            print("   → Assigning to: Automation Team")
            print("   → Next: Execute remediation workflow")

            # In real integration, you would:
            # - Update ServiceNow incident with work note
            # - Assign to automation team
            # - Trigger remediation automation

        else:
            print("🔴 LOW CONFIDENCE - Routing to Human Escalation Path")
            print("   → Requires human review")
            print("   → Assigning to: SRE On-Call")
            print("   → Priority: Escalated")

            # In real integration, you would:
            # - Update ServiceNow incident with work note
            # - Increase priority
            # - Assign to SRE on-call
            # - Send notification to SRE team

        print()

    except Exception as e:
        print(f"❌ Error triggering A.E.G.I.S.: {e}")
        print("Falling back to manual triage")


def direct_api_example():
    """
    Alternative: Call A.E.G.I.S. API directly (without Orchestrate SDK)

    This is simpler and works with Trial plans.
    """
    import requests

    print("=" * 70)
    print("Direct API Integration Example")
    print("=" * 70)
    print()

    # A.E.G.I.S. Decision Service endpoint
    aegis_url = "https://your-aegis-service-url.codeengine.appdomain.cloud/evaluate-incident"

    # Example incident
    incident = {
        "incident_text": "Database latency is high but system metrics look normal.",
        "category": "latency"
    }

    print(f"Calling A.E.G.I.S. API: {aegis_url}")
    print(f"Input: {incident['incident_text']}")
    print()

    try:
        response = requests.post(aegis_url, json=incident, timeout=30)
        response.raise_for_status()

        result = response.json()

        print("✅ Response received:")
        print(f"   Confidence: {result.get('confidence_score')}%")
        print(f"   Action: {result.get('recommended_action')}")
        print(f"   Analysis: {result.get('analysis')}")
        print()

        return result

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


if __name__ == "__main__":
    print("\n🎯 A.E.G.I.S. Orchestrate SDK Integration Examples\n")

    # Check if API key is configured
    if not ORCHESTRATE_API_KEY:
        print("⚠️  ORCHESTRATE_API_KEY not set")
        print("   Using Direct API example instead...\n")

        # Run direct API example (works without Orchestrate credentials)
        direct_api_example()
    else:
        # Run full Orchestrate SDK example
        servicenow_integration_example()

    print("\n" + "=" * 70)
    print("Integration Pattern Summary")
    print("=" * 70)
    print("""
    ServiceNow Incident Created
        ↓
    Trigger via Orchestrate SDK or Direct API
        ↓
    A.E.G.I.S. analyzes with watsonx.ai Granite
        ↓
    Returns confidence score & recommendation
        ↓
    IF confidence >= 80:
        → Route to automation (clear_logs, restart_service, etc.)
    ELSE:
        → Route to human (escalate, run_diagnostics)
    """)
