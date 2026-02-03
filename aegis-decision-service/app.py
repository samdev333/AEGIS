"""
A.E.G.I.S. Decision Service
Automated Escalation & Governance Intelligence System

This service provides AI-powered incident analysis using IBM watsonx.ai Granite models.
It evaluates incidents and returns structured decisions with confidence scores for
watsonx Orchestrate to route appropriately.
"""

import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for watsonx Orchestrate integration

# --- IBM Cloud Credentials ---
# Load from environment variables for security
credentials = {
    "url": os.environ.get("WATSONX_URL", "https://us-south.ml.cloud.ibm.com"),
    "apikey": os.environ.get("IBM_CLOUD_API_KEY")
}
project_id = os.environ.get("WATSONX_PROJECT_ID")

# Validate configuration
if not credentials["apikey"]:
    logger.warning("IBM_CLOUD_API_KEY not set. Service will fail on inference.")
if not project_id:
    logger.warning("WATSONX_PROJECT_ID not set. Service will fail on inference.")

# --- System Prompt (The "Judge Gold" Prompt) ---
SYSTEM_PROMPT_TEMPLATE = """<|system|>
You are an enterprise Site Reliability Engineer AI agent for the A.E.G.I.S. system.

Your job is to analyze incident reports and provide structured decision recommendations.

CRITICAL RULES:
1. Respond ONLY with valid JSON - no additional text or explanation outside the JSON
2. If the incident is ambiguous, missing critical data, or involves high risk → confidence_score MUST be < 50
3. If confidence_score < 80 → recommended_action MUST be 'escalate_to_human'
4. Always prefer safety over automation
5. Valid actions are ONLY: ["clear_logs", "restart_service", "run_diagnostics", "escalate_to_human"]

Response Format (strict JSON):
{{
  "analysis": "one sentence summary of the incident",
  "recommended_action": "action_name",
  "confidence_score": 0-100,
  "explanation": "short explanation for human reviewer"
}}

{context}
<|user|>
Incident Report: {incident_text}
<|assistant|>
"""


def get_runbook_context(category):
    """
    Simulate Langflow runbook context retrieval.
    In production, this would call a Langflow endpoint or vector DB.
    """
    runbooks = {
        "latency": [
            "Check network latency to database",
            "Review recent query execution times",
            "Check for lock contention in DB"
        ],
        "storage": [
            "Check disk space usage on all volumes",
            "Review log rotation configuration",
            "Identify large files or orphaned data"
        ],
        "auth": [
            "Verify authentication service health",
            "Check token expiration policies",
            "Review recent failed login attempts"
        ],
        "unknown": [
            "Gather complete system metrics",
            "Check application logs for errors",
            "Verify all critical services are running"
        ]
    }

    context_steps = runbooks.get(category.lower(), runbooks["unknown"])
    return "\n".join([f"- {step}" for step in context_steps])


def get_granite_decision(incident_text, category="unknown", runbook_context=None):
    """
    Call IBM watsonx.ai Granite model to analyze incident and return decision.

    Args:
        incident_text (str): The incident description
        category (str): Incident category for context retrieval
        runbook_context (str): Optional pre-fetched runbook context

    Returns:
        dict: Structured decision with analysis, action, confidence, and explanation
    """
    try:
        # Get runbook context if not provided
        if runbook_context is None:
            runbook_context = get_runbook_context(category)

        context_block = f"""
Relevant Runbook Context:
{runbook_context}

Use this context to inform your analysis.
"""

        # Build the complete prompt
        prompt = SYSTEM_PROMPT_TEMPLATE.format(
            incident_text=incident_text,
            context=context_block
        )

        # Initialize the Granite model
        model = Model(
            model_id="ibm/granite-3-8b-instruct",  # Using Granite 3 8B Instruct
            params={
                GenParams.DECODING_METHOD: "greedy",
                GenParams.MAX_NEW_TOKENS: 400,
                GenParams.MIN_NEW_TOKENS: 50,
                GenParams.TEMPERATURE: 0.1,  # Low temperature for consistent JSON
                GenParams.STOP_SEQUENCES: ["<|endoftext|>"]
            },
            credentials=credentials,
            project_id=project_id
        )

        logger.info(f"Sending incident to Granite for analysis: {incident_text[:100]}...")

        # Generate response
        response = model.generate_text(prompt=prompt)

        logger.info(f"Raw Granite response: {response[:200]}...")

        # Parse JSON response
        # Try to extract JSON from the response (sometimes models add extra text)
        response = response.strip()

        # Find JSON object boundaries
        start_idx = response.find('{')
        end_idx = response.rfind('}')

        if start_idx == -1 or end_idx == -1:
            raise ValueError("No JSON object found in response")

        json_str = response[start_idx:end_idx + 1]
        decision = json.loads(json_str)

        # Validate required fields
        required_fields = ["analysis", "recommended_action", "confidence_score", "explanation"]
        for field in required_fields:
            if field not in decision:
                raise ValueError(f"Missing required field: {field}")

        # Validate confidence_score is integer
        decision["confidence_score"] = int(decision["confidence_score"])

        # Validate action is one of the allowed values
        valid_actions = ["clear_logs", "restart_service", "run_diagnostics", "escalate_to_human"]
        if decision["recommended_action"] not in valid_actions:
            logger.warning(f"Invalid action {decision['recommended_action']}, defaulting to escalate_to_human")
            decision["recommended_action"] = "escalate_to_human"
            decision["confidence_score"] = min(decision["confidence_score"], 50)

        logger.info(f"Decision: {decision['recommended_action']} (confidence: {decision['confidence_score']})")

        return decision

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        logger.error(f"Response was: {response}")
        # Return safe fallback
        return {
            "analysis": "Unable to parse AI response",
            "recommended_action": "escalate_to_human",
            "confidence_score": 0,
            "explanation": "System encountered an error parsing the AI decision. Human review required."
        }
    except Exception as e:
        logger.error(f"Error calling Granite model: {e}")
        # Return safe fallback
        return {
            "analysis": f"System error during analysis",
            "recommended_action": "escalate_to_human",
            "confidence_score": 0,
            "explanation": f"System error: {str(e)}. Escalating to human for safety."
        }


@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "service": "A.E.G.I.S. Decision Service",
        "status": "healthy",
        "version": "1.0.0",
        "endpoints": [
            "POST /evaluate-incident - Evaluate an incident and get decision recommendation"
        ]
    })


@app.route('/evaluate-incident', methods=['POST'])
def evaluate_incident():
    """
    Main endpoint for incident evaluation.

    Expected JSON input:
    {
        "incident_text": "Description of the incident",
        "category": "latency | storage | auth | unknown"  (optional)
    }

    Returns JSON:
    {
        "analysis": "summary",
        "recommended_action": "action",
        "confidence_score": 0-100,
        "explanation": "explanation"
    }
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                "error": "Request must be JSON",
                "status": "error"
            }), 400

        data = request.json

        # Extract incident text
        incident_text = data.get("incident_text", "").strip()
        if not incident_text:
            return jsonify({
                "error": "incident_text is required and cannot be empty",
                "status": "error"
            }), 400

        # Extract optional category
        category = data.get("category", "unknown")

        # Optional: allow custom runbook context
        runbook_context = data.get("runbook_context")

        logger.info(f"Evaluating incident (category: {category})")

        # Get decision from Granite
        decision = get_granite_decision(incident_text, category, runbook_context)

        # Add metadata
        decision["status"] = "success"
        decision["incident_text"] = incident_text
        decision["category"] = category

        return jsonify(decision), 200

    except Exception as e:
        logger.error(f"Error in evaluate_incident endpoint: {e}")
        return jsonify({
            "error": str(e),
            "status": "error",
            "analysis": "System error",
            "recommended_action": "escalate_to_human",
            "confidence_score": 0,
            "explanation": "An unexpected error occurred. Escalating to human for safety."
        }), 500


@app.route('/test-connection', methods=['GET'])
def test_connection():
    """
    Test endpoint to verify watsonx.ai connection.
    """
    try:
        if not credentials["apikey"] or not project_id:
            return jsonify({
                "status": "error",
                "message": "Missing API key or project ID. Check environment variables."
            }), 500

        # Try a simple model initialization
        model = Model(
            model_id="ibm/granite-3-8b-instruct",
            params={GenParams.MAX_NEW_TOKENS: 10},
            credentials=credentials,
            project_id=project_id
        )

        # Simple test generation
        response = model.generate_text(prompt="Hello")

        return jsonify({
            "status": "success",
            "message": "Successfully connected to watsonx.ai",
            "model": "ibm/granite-3-8b-instruct",
            "test_response": response[:50]
        }), 200

    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return jsonify({
            "status": "error",
            "message": f"Connection test failed: {str(e)}"
        }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
