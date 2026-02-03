"""
watsonx.ai Client Wrapper for A.E.G.I.S.

Handles all interactions with IBM watsonx.ai Granite models.
Provides robust JSON parsing with fallback mechanisms.
"""

import os
import json
import logging
import re
from typing import Optional
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

from .models import ModelDecision

logger = logging.getLogger(__name__)

# Configuration from environment
WATSONX_APIKEY = os.environ.get("WATSONX_APIKEY")
WATSONX_URL = os.environ.get("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
WATSONX_PROJECT_ID = os.environ.get("WATSONX_PROJECT_ID")
WATSONX_MODEL_ID = os.environ.get("WATSONX_MODEL_ID", "ibm/granite-3-8b-instruct")
MOCK_WATSONX = os.environ.get("MOCK_WATSONX", "0") == "1"


class WatsonxClient:
    """
    Client for IBM watsonx.ai Granite models.

    Handles model initialization, prompt construction, and response parsing
    with robust error handling and fallback mechanisms.
    """

    SYSTEM_PROMPT_TEMPLATE = """<|system|>
You are an enterprise Site Reliability Engineer AI agent for the A.E.G.I.S. system.

Your job is to analyze incident reports and provide structured decision recommendations.

CRITICAL RULES:
1. Respond ONLY with valid JSON - absolutely no additional text, explanation, markdown fences, or commentary
2. The JSON must contain exactly these 4 fields: analysis, recommended_action, confidence_score, explanation
3. Valid recommended_action values are ONLY: clear_logs, restart_service, run_diagnostics, escalate_to_human
4. Always prefer safety over automation

AMBIGUITY AND CONFLICT DETECTION:
- If the incident describes symptoms but lacks clear causal signals (e.g., "latency high but metrics normal"), treat it as AMBIGUOUS:
  * confidence_score MUST be between 30 and 60
  * recommended_action MUST be "escalate_to_human" OR "run_diagnostics"
- If there are conflicting indicators (e.g., "high latency" with "low CPU", "error" with "normal metrics"):
  * confidence_score MUST be <= 60
  * recommended_action MUST be "escalate_to_human" OR "run_diagnostics"
- If incident mentions multiple possible root causes without clear evidence:
  * confidence_score MUST be <= 60

CONFIDENCE SCORING RUBRIC:
- 90-100: Clear, common issue with strong indicators and low risk. All key signals align.
- 70-89: Likely issue but missing 1-2 key confirming signals or minor ambiguity.
- 30-69: Ambiguous, conflicting signals, OR multiple plausible root causes.
- 0-29: Unknown, high risk, insufficient information, or safety-critical uncertainty.

POLICY ENFORCEMENT:
- If confidence_score < 80 → recommended_action MUST be "escalate_to_human" OR "run_diagnostics"
- If confidence_score < 90 → Do NOT use language implying auto-resolution (e.g., "can be auto-resolved", "will be resolved automatically")
- If confidence_score < 90 → explanation should recommend diagnostics or human review, not claim resolution

Response Format (STRICT JSON - NO OTHER TEXT OR MARKDOWN):
{{
  "analysis": "one sentence summary of the incident",
  "recommended_action": "clear_logs|restart_service|run_diagnostics|escalate_to_human",
  "confidence_score": 0-100,
  "explanation": "short explanation for human reviewer"
}}

{runbook_context}
<|user|>
Incident Report:
{incident_text}

Reporter Role: {reporter_role}
Category: {category}
<|assistant|>
"""

    def __init__(self):
        """Initialize the watsonx.ai client"""
        self.credentials = {
            "url": WATSONX_URL,
            "apikey": WATSONX_APIKEY
        }
        self.project_id = WATSONX_PROJECT_ID
        self.model_id = WATSONX_MODEL_ID
        self.mock_mode = MOCK_WATSONX

        # Validate configuration
        if not MOCK_WATSONX:
            if not WATSONX_APIKEY:
                logger.warning("WATSONX_APIKEY not set - client will fail on inference")
            if not WATSONX_PROJECT_ID:
                logger.warning("WATSONX_PROJECT_ID not set - client will fail on inference")

        if self.mock_mode:
            logger.info("WatsonxClient initialized in MOCK MODE")
        else:
            logger.info(f"Initialized WatsonxClient with model: {self.model_id}")

    def get_decision(
        self,
        incident_text: str,
        category: str,
        reporter_role: str,
        runbook_context: str
    ) -> ModelDecision:
        """
        Get decision from Granite model with robust error handling.

        Args:
            incident_text: The incident description
            category: Incident category
            reporter_role: Reporter's role
            runbook_context: Formatted runbook context

        Returns:
            ModelDecision object

        Raises:
            Exception: Only if credentials are missing or model initialization fails
        """
        try:
            # Build prompt
            prompt = self._build_prompt(
                incident_text=incident_text,
                category=category,
                reporter_role=reporter_role,
                runbook_context=runbook_context
            )

            # Get response (mocked or real)
            if self.mock_mode:
                logger.info("Using MOCK response")
                raw_response = self._get_mock_response(incident_text)
            else:
                # Initialize model
                model = self._initialize_model()

                # Generate response
                logger.info(f"Sending request to {self.model_id}")
                raw_response = model.generate_text(prompt=prompt)
                logger.info(f"Received response from model (length: {len(raw_response)})")

            # Parse response with fallback
            decision = self._parse_response(raw_response)

            # Validate decision with ambiguity detection
            decision = self._validate_decision(decision, incident_text)

            return decision

        except Exception as e:
            logger.error(f"Error in get_decision: {e}", exc_info=True)
            # Return safe fallback
            return self._get_fallback_decision(str(e))

    def _get_mock_response(self, incident_text: str) -> str:
        """
        Return mock responses for testing.

        Simulates both clean JSON and JSON with extra text.
        """
        incident_lower = incident_text.lower()

        # Ambiguous incident pattern
        if ("but" in incident_lower and "normal" in incident_lower) or \
           ("high" in incident_lower and "metrics" in incident_lower and "normal" in incident_lower):
            return '''
Here's the analysis:
{
  "analysis": "Database latency elevated but system metrics appear normal",
  "recommended_action": "run_diagnostics",
  "confidence_score": 50,
  "explanation": "Conflicting signals detected: high latency but normal metrics. Requires diagnostic investigation to identify root cause."
}
Hope this helps!
'''

        # Clear disk space issue
        if "disk" in incident_lower and ("99" in incident_text or "95" in incident_text):
            return '{"analysis": "Disk space critically low on server", "recommended_action": "clear_logs", "confidence_score": 95, "explanation": "Clear disk space issue with standard remediation available. Low risk for automated cleanup."}'

        # Default ambiguous case
        return {
            "analysis": "Incident requires investigation",
            "recommended_action": "escalate_to_human",
            "confidence_score": 40,
            "explanation": "Insufficient information to determine root cause confidently. Escalating for human review."
        }

    def _build_prompt(
        self,
        incident_text: str,
        category: str,
        reporter_role: str,
        runbook_context: str
    ) -> str:
        """Build the complete prompt for the model"""
        return self.SYSTEM_PROMPT_TEMPLATE.format(
            incident_text=incident_text,
            category=category,
            reporter_role=reporter_role,
            runbook_context=runbook_context
        )

    def _initialize_model(self) -> Model:
        """Initialize the watsonx.ai model"""
        return Model(
            model_id=self.model_id,
            params={
                GenParams.DECODING_METHOD: "greedy",
                GenParams.MAX_NEW_TOKENS: 500,
                GenParams.MIN_NEW_TOKENS: 50,
                GenParams.TEMPERATURE: 0.1,  # Low temperature for consistent JSON
                GenParams.STOP_SEQUENCES: ["<|endoftext|>", "<|user|>"]
            },
            credentials=self.credentials,
            project_id=self.project_id
        )

    def _parse_response(self, raw_response: str) -> ModelDecision:
        """
        Parse model response with robust JSON extraction.

        Strategies:
        1. Direct JSON parse
        2. Extract JSON from markdown code blocks
        3. Find JSON object boundaries and extract
        4. Regex field extraction
        5. Fallback to safe decision

        Args:
            raw_response: Raw model output

        Returns:
            ModelDecision object
        """
        # Handle dict input from mock
        if isinstance(raw_response, dict):
            return self._create_model_decision(raw_response)

        # Strategy 1: Direct parse
        try:
            data = json.loads(raw_response.strip())
            return self._create_model_decision(data)
        except (json.JSONDecodeError, TypeError):
            pass

        # Strategy 2: Extract from markdown code blocks
        code_block_pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
        match = re.search(code_block_pattern, raw_response, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                return self._create_model_decision(data)
            except json.JSONDecodeError:
                pass

        # Strategy 3: Find JSON object boundaries
        start_idx = raw_response.find('{')
        end_idx = raw_response.rfind('}')

        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_str = raw_response[start_idx:end_idx + 1]
            try:
                data = json.loads(json_str)
                return self._create_model_decision(data)
            except json.JSONDecodeError:
                pass

        # Strategy 4: Try to find each field with regex
        logger.warning("All JSON parsing strategies failed, attempting regex extraction")
        try:
            return self._extract_with_regex(raw_response)
        except Exception as e:
            logger.error(f"Regex extraction failed: {e}")

        # Final fallback
        logger.error(f"Could not parse response: {raw_response[:200]}")
        return self._get_fallback_decision("Unable to parse model response as JSON")

    def _extract_with_regex(self, text: str) -> ModelDecision:
        """Last resort: extract fields using regex"""
        analysis_match = re.search(r'"analysis"\s*:\s*"([^"]+)"', text)
        action_match = re.search(r'"recommended_action"\s*:\s*"([^"]+)"', text)
        confidence_match = re.search(r'"confidence_score"\s*:\s*(\d+)', text)
        explanation_match = re.search(r'"explanation"\s*:\s*"([^"]+)"', text)

        if not all([analysis_match, action_match, confidence_match, explanation_match]):
            raise ValueError("Could not extract required fields with regex")

        return ModelDecision(
            analysis=analysis_match.group(1),
            recommended_action=action_match.group(1),
            confidence_score=int(confidence_match.group(1)),
            explanation=explanation_match.group(1)
        )

    def _create_model_decision(self, data: dict) -> ModelDecision:
        """Create ModelDecision from parsed JSON data"""
        required_fields = ["analysis", "recommended_action", "confidence_score", "explanation"]

        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Ensure confidence_score is integer
        confidence = data["confidence_score"]
        if isinstance(confidence, str):
            confidence = int(confidence)

        return ModelDecision(
            analysis=data["analysis"],
            recommended_action=data["recommended_action"],
            confidence_score=confidence,
            explanation=data["explanation"]
        )

    def _detect_ambiguity(self, incident_text: str) -> bool:
        """
        Detect ambiguous or conflicting signals in incident text.

        Returns True if incident appears ambiguous.
        """
        text_lower = incident_text.lower()

        # Pattern 1: "but normal" or similar contradictions
        if re.search(r'\b(but|however|although)\b.*\bnormal\b', text_lower):
            return True

        # Pattern 2: High symptom with low/normal metric
        high_symptom = re.search(r'\b(high|elevated|increased|spike)\b', text_lower)
        normal_metric = re.search(r'\b(normal|low|stable|within range)\b', text_lower)
        if high_symptom and normal_metric:
            return True

        # Pattern 3: Multiple "may be" / "could be" / "possibly"
        uncertainty_count = len(re.findall(r'\b(may|might|could|possibly|unclear|unknown|intermittent)\b', text_lower))
        if uncertainty_count >= 2:
            return True

        # Pattern 4: "no clear pattern" or similar
        if re.search(r'\bno (clear|obvious|apparent) (pattern|cause|reason|indicator)', text_lower):
            return True

        return False

    def _validate_decision(self, decision: ModelDecision, incident_text: str) -> ModelDecision:
        """
        Validate and enforce decision policy with ambiguity detection.

        Rules:
        - Valid actions: clear_logs, restart_service, run_diagnostics, escalate_to_human
        - If confidence < 80, action must be escalate_to_human or run_diagnostics
        - If ambiguity detected, cap confidence at 60
        - If confidence < 90, explanation must not imply auto-resolution
        - Confidence must be 0-100
        """
        valid_actions = ["clear_logs", "restart_service", "run_diagnostics", "escalate_to_human"]

        # Validate action
        if decision.recommended_action not in valid_actions:
            logger.warning(f"Invalid action '{decision.recommended_action}', forcing escalation")
            decision.recommended_action = "escalate_to_human"
            decision.confidence_score = min(decision.confidence_score, 10)

        # Detect ambiguity in incident text
        is_ambiguous = self._detect_ambiguity(incident_text)
        if is_ambiguous:
            logger.info("Ambiguity detected in incident text")
            # Cap confidence at 60 for ambiguous incidents
            if decision.confidence_score > 60:
                logger.warning(f"Ambiguous incident but confidence was {decision.confidence_score}, capping at 60")
                decision.confidence_score = 60

            # Force safe action
            if decision.recommended_action not in ["escalate_to_human", "run_diagnostics"]:
                logger.warning(f"Ambiguous incident but action was '{decision.recommended_action}', forcing escalation")
                decision.recommended_action = "escalate_to_human"

        # Enforce confidence threshold policy
        if decision.confidence_score < 80:
            if decision.recommended_action not in ["escalate_to_human", "run_diagnostics"]:
                logger.warning(
                    f"Low confidence ({decision.confidence_score}) but action is "
                    f"'{decision.recommended_action}'. Forcing escalation."
                )
                decision.recommended_action = "escalate_to_human"

        # Check for auto-resolution language with confidence < 90
        if decision.confidence_score < 90:
            auto_resolve_patterns = [
                r'\bauto[\s-]?resolv',
                r'\bresolved automatically\b',
                r'\bcan be resolved\b.*\bautomatically\b',
                r'\bwill be resolved\b'
            ]
            explanation_lower = decision.explanation.lower()
            for pattern in auto_resolve_patterns:
                if re.search(pattern, explanation_lower):
                    logger.warning(f"Confidence < 90 but explanation implies auto-resolution. Updating explanation.")
                    decision.explanation = decision.explanation + " Requires review before execution."
                    break

        # Clamp confidence score
        decision.confidence_score = max(0, min(100, decision.confidence_score))

        return decision

    def _get_fallback_decision(self, error_message: str) -> ModelDecision:
        """
        Safe fallback decision when all else fails.

        Always escalates to human with minimal confidence.
        """
        logger.error("Returning safe fallback decision")
        return ModelDecision(
            analysis="System error during AI analysis",
            recommended_action="escalate_to_human",
            confidence_score=10,
            explanation=f"An error occurred during analysis. Human review required. Error: {error_message[:100]}"
        )

    def test_connection(self) -> bool:
        """
        Test connection to watsonx.ai.

        Returns:
            True if connection successful, False otherwise
        """
        if self.mock_mode:
            logger.info("Mock mode enabled, connection test skipped")
            return True

        try:
            model = self._initialize_model()
            response = model.generate_text(prompt="Test", params={GenParams.MAX_NEW_TOKENS: 5})
            logger.info("Connection test successful")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
