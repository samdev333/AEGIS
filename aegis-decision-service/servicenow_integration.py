#!/usr/bin/env python3
"""
ServiceNow → A.E.G.I.S. Integration Example

This script demonstrates how to integrate A.E.G.I.S. Decision Service
with ServiceNow for automated incident triage.

Works without Orchestrate SDK - uses direct REST API calls.
"""

import requests
import json
from typing import Dict, Any


# A.E.G.I.S. Configuration
AEGIS_URL = "https://your-aegis-service-url.codeengine.appdomain.cloud/evaluate-incident"


def call_aegis_decision_service(incident_text: str, category: str = "unknown") -> Dict[str, Any]:
    """
    Call A.E.G.I.S. Decision Service API.

    Args:
        incident_text: Description of the incident
        category: Incident category (latency, storage, auth, unknown)

    Returns:
        dict: Analysis result with confidence_score, recommended_action, etc.
    """
    payload = {
        "incident_text": incident_text,
        "category": category
    }

    try:
        response = requests.post(
            AEGIS_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error calling A.E.G.I.S.: {e}")
        # Return safe fallback
        return {
            "analysis": "Service unavailable",
            "recommended_action": "escalate_to_human",
            "confidence_score": 0,
            "explanation": f"Could not reach A.E.G.I.S. service: {str(e)}"
        }


def process_servicenow_incident(incident_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a ServiceNow incident through A.E.G.I.S.

    Args:
        incident_data: ServiceNow incident object

    Returns:
        dict: Processing result with recommendation
    """

    # Extract incident details
    incident_number = incident_data.get("number", "UNKNOWN")
    short_desc = incident_data.get("short_description", "")
    full_desc = incident_data.get("description", "")
    priority = incident_data.get("priority", "")
    sn_category = incident_data.get("category", "")

    # Combine descriptions for analysis
    combined_text = f"{short_desc}. {full_desc}".strip()

    # Map ServiceNow category to A.E.G.I.S. category
    category_mapping = {
        "Database": "latency",
        "Storage": "storage",
        "Authentication": "auth",
        "Network": "latency",
        "Application": "unknown"
    }
    aegis_category = category_mapping.get(sn_category, "unknown")

    print(f"\n{'='*70}")
    print(f"Processing Incident: {incident_number}")
    print(f"{'='*70}")
    print(f"Description: {short_desc}")
    print(f"Priority: {priority}")
    print(f"Category: {sn_category} → {aegis_category}")
    print()

    # Call A.E.G.I.S.
    print("🤖 Calling A.E.G.I.S. Decision Service...")
    result = call_aegis_decision_service(combined_text, aegis_category)

    # Extract results
    confidence = result.get("confidence_score", 0)
    action = result.get("recommended_action", "escalate_to_human")
    analysis = result.get("analysis", "")
    explanation = result.get("explanation", "")

    print(f"\n📊 A.E.G.I.S. Analysis:")
    print(f"   Confidence Score: {confidence}%")
    print(f"   Recommended Action: {action}")
    print(f"   Analysis: {analysis}")
    print(f"   Explanation: {explanation}")
    print()

    # Decision routing based on confidence
    if confidence >= 80:
        print("✅ HIGH CONFIDENCE - Auto-Execute Path")
        print(f"   → Action: {action}")
        print("   → Next: Route to automation workflow")

        # What you would do in real integration:
        recommendation = {
            "route": "automation",
            "assignment_group": "Automation Team",
            "state": "In Progress",
            "work_note": f"[A.E.G.I.S. Auto-Triage] Confidence: {confidence}% - {analysis}. Recommended action: {action}.",
            "priority": priority,  # Keep current priority
            "next_action": action
        }

    else:
        print("⚠️  LOW CONFIDENCE - Human Escalation Path")
        print("   → Requires expert review")
        print("   → Next: Route to SRE on-call")

        # What you would do in real integration:
        recommendation = {
            "route": "human_escalation",
            "assignment_group": "SRE On-Call",
            "state": "Awaiting Review",
            "work_note": f"[A.E.G.I.S. Auto-Triage] Confidence: {confidence}% - Requires human review. {explanation}",
            "priority": "1-High",  # Escalate priority
            "next_action": "escalate_to_human"
        }

    return {
        "incident_number": incident_number,
        "aegis_result": result,
        "recommendation": recommendation
    }


def servicenow_business_rule_simulation():
    """
    Simulates what would happen in a ServiceNow Business Rule.

    This code would be adapted to ServiceNow's server-side JavaScript.
    """

    # Example 1: Ambiguous incident (Prompt v2 feature)
    print("\n" + "="*70)
    print("TEST 1: Ambiguous Incident (Conflicting Signals)")
    print("="*70)

    incident_1 = {
        "number": "INC0012345",
        "short_description": "Database latency is high but system metrics look normal",
        "description": "Users reporting slow query times. Database latency at 5000ms. CPU 20%, Memory 45%, Disk I/O normal.",
        "priority": "2-Medium",
        "category": "Database",
        "state": "New"
    }

    result_1 = process_servicenow_incident(incident_1)
    print(f"\n💡 Recommendation for ServiceNow:")
    print(json.dumps(result_1["recommendation"], indent=2))


    # Example 2: Clear incident
    print("\n" + "="*70)
    print("TEST 2: Clear Incident (High Confidence)")
    print("="*70)

    incident_2 = {
        "number": "INC0012346",
        "short_description": "Disk space at 99% on Server-DB-01",
        "description": "/var/log directory consuming 95GB. Log rotation appears to have failed. No user impact yet.",
        "priority": "2-Medium",
        "category": "Storage",
        "state": "New"
    }

    result_2 = process_servicenow_incident(incident_2)
    print(f"\n💡 Recommendation for ServiceNow:")
    print(json.dumps(result_2["recommendation"], indent=2))


def generate_servicenow_business_rule():
    """
    Generate ServiceNow Business Rule code.

    Copy this into ServiceNow: System Definition → Business Rules
    """

    business_rule_code = '''
// ServiceNow Business Rule: A.E.G.I.S. Auto-Triage
// Table: incident
// When: after insert
// Conditions: Priority is High OR Medium, State is New

(function executeRule(current, previous) {

    try {
        // A.E.G.I.S. Decision Service endpoint
        var aegisUrl = 'https://your-aegis-service-url.codeengine.appdomain.cloud/evaluate-incident';

        // Prepare request
        var request = new sn_ws.RESTMessageV2();
        request.setEndpoint(aegisUrl);
        request.setHttpMethod('POST');
        request.setRequestHeader('Content-Type', 'application/json');

        // Build payload
        var payload = {
            incident_text: current.short_description + ". " + current.description,
            category: mapCategory(current.category)
        };
        request.setRequestBody(JSON.stringify(payload));

        // Execute request (asynchronously to avoid blocking)
        var response = request.executeAsync();

        // Process response (in callback)
        response.waitForResponse(30); // Wait up to 30 seconds

        if (response.getStatusCode() == 200) {
            var result = JSON.parse(response.getBody());

            // Add work note with AI analysis
            var workNote = "[A.E.G.I.S. Auto-Triage]\\n";
            workNote += "Confidence: " + result.confidence_score + "%\\n";
            workNote += "Analysis: " + result.analysis + "\\n";
            workNote += "Recommended: " + result.recommended_action + "\\n";
            workNote += "Explanation: " + result.explanation;

            current.work_notes = workNote;

            // Route based on confidence
            if (result.confidence_score >= 80) {
                // High confidence - route to automation
                current.assignment_group = getGroupSysId('Automation Team');
                current.state = 2; // In Progress
            } else {
                // Low confidence - escalate to human
                current.assignment_group = getGroupSysId('SRE On-Call');
                current.priority = 1; // Escalate priority
                current.state = 1; // New (awaiting review)
            }

            current.update();

            gs.info('A.E.G.I.S. triage completed for ' + current.number);
        }

    } catch (ex) {
        gs.error('A.E.G.I.S. integration error: ' + ex);
        // Fail gracefully - incident remains in manual queue
    }

    // Helper function to map categories
    function mapCategory(sn_category) {
        var mapping = {
            'Database': 'latency',
            'Storage': 'storage',
            'Authentication': 'auth',
            'Network': 'latency'
        };
        return mapping[sn_category] || 'unknown';
    }

    // Helper function to get group sys_id
    function getGroupSysId(groupName) {
        var gr = new GlideRecord('sys_user_group');
        gr.addQuery('name', groupName);
        gr.query();
        if (gr.next()) {
            return gr.sys_id;
        }
        return null;
    }

})(current, previous);
'''

    print("\n" + "="*70)
    print("ServiceNow Business Rule Code")
    print("="*70)
    print(business_rule_code)

    # Save to file
    with open("servicenow_business_rule.js", "w") as f:
        f.write(business_rule_code)
    print("\n✅ Business Rule saved to: servicenow_business_rule.js")


if __name__ == "__main__":
    print("\n🎯 A.E.G.I.S. → ServiceNow Integration\n")

    # Run test scenarios
    servicenow_business_rule_simulation()

    # Generate ServiceNow code
    generate_servicenow_business_rule()

    print("\n" + "="*70)
    print("Summary")
    print("="*70)
    print("""
✅ A.E.G.I.S. Decision Service is ready for ServiceNow integration!

Integration Options:
1. Direct REST API (Recommended for Trial plan)
2. ServiceNow Business Rule (copy servicenow_business_rule.js)
3. ServiceNow Flow Designer (low-code option)

Next Steps:
1. Copy servicenow_business_rule.js into ServiceNow
2. Configure assignment groups
3. Test with sample incidents
4. Monitor confidence score distribution
    """)
