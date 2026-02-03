# A.E.G.I.S. Decision Service - Complete Project Context

## Overview
AI-powered incident evaluation service deployed to IBM Cloud Code Engine that analyzes IT incidents and provides confidence-scored recommendations.

## Deployment Details
- **Production URL**: `https://your-aegis-service-url.codeengine.appdomain.cloud`
- **Endpoint**: `/evaluate-incident` (POST)
- **Region**: eu-gb (London)
- **Platform**: IBM Cloud Code Engine

## API Specification

### Request
```json
POST /evaluate-incident
Content-Type: application/json

{
  "incident_text": "Description of the incident",
  "category": "optional category"
}
```

### Response
```json
{
  "recommended_action": "string - the recommended action to take",
  "confidence": 0-100,
  "reasoning": "string - explanation of the decision",
  "runbook_used": "string - which runbook was referenced",
  "requires_human_review": true/false
}
```

### Decision Logic
- **Confidence >= 80**: Auto-resolution eligible
- **Confidence < 80**: Requires human review
- **Ambiguous incidents**: Capped at confidence <= 60

## Key Files

### src/aegis_service/watsonx_client.py
Core logic with:
- Prompt v2 with ambiguity detection
- `_detect_ambiguity()` - Pattern matching for conflicting signals
- `_validate_decision()` - Confidence capping for ambiguous cases
- Mock mode via `MOCK_WATSONX=1` environment variable

### Ambiguity Detection Patterns
```python
def _detect_ambiguity(self, incident_text: str) -> bool:
    text_lower = incident_text.lower()

    # Pattern 1: "but normal" contradictions
    if re.search(r'\b(but|however|although)\b.*\bnormal\b', text_lower):
        return True

    # Pattern 2: High symptom with normal metric
    high_symptom = re.search(r'\b(high|elevated|increased|spike)\b', text_lower)
    normal_metric = re.search(r'\b(normal|low|stable|within range)\b', text_lower)
    if high_symptom and normal_metric:
        return True

    # Pattern 3: Multiple uncertainty markers
    uncertainty_count = len(re.findall(
        r'\b(may|might|could|possibly|unclear|unknown|intermittent)\b', text_lower))
    if uncertainty_count >= 2:
        return True

    return False
```

## Integration Examples

### ServiceNow Business Rule
```python
import requests

AEGIS_URL = "https://your-aegis-service-url.codeengine.appdomain.cloud/evaluate-incident"

def call_aegis(incident_text: str, category: str = "unknown"):
    payload = {"incident_text": incident_text, "category": category}
    response = requests.post(AEGIS_URL, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()

# Example usage
result = call_aegis("Server CPU high but all metrics show normal")
if result["requires_human_review"]:
    # Escalate to human
    pass
else:
    # Auto-resolve using recommended_action
    pass
```

### cURL Test Commands
```bash
# Test ambiguous incident (should get confidence <= 60)
curl -X POST https://your-aegis-service-url.codeengine.appdomain.cloud/evaluate-incident \
  -H "Content-Type: application/json" \
  -d '{"incident_text": "Server latency is high but all metrics show normal", "category": "performance"}'

# Test clear incident (should get confidence >= 80)
curl -X POST https://your-aegis-service-url.codeengine.appdomain.cloud/evaluate-incident \
  -H "Content-Type: application/json" \
  -d '{"incident_text": "Disk space critically low at 95% on production server", "category": "storage"}'
```

## IBM Cloud Credentials
- **IBM Cloud API Key**: `your_ibm_cloud_api_key_here`
- **watsonx Project ID**: `your_watsonx_project_id_here`
- **watsonx.ai Region**: us-south
- **Code Engine Region**: eu-gb

## watsonx Orchestrate Setup
- **Environment**: watsonx-hackathon
- **API URL**: `https://api.eu-gb.watson-orchestrate.cloud.ibm.com`
- **CLI Location**: `orchestrate.exe`

## Local Development

### Run with Mock Mode (no API calls)
```bash
set MOCK_WATSONX=1
uvicorn src.aegis_service.main:app --reload
```

### Run Tests
```bash
set MOCK_WATSONX=1
python test_ambiguity.py
```

### Deploy to IBM Cloud
```bash
ibmcloud target -r eu-gb
ibmcloud ce project select --name aegis-project
ibmcloud ce buildrun submit --build aegis-decision-service-build --wait
```

## Technology Stack
- **Runtime**: Python 3.11+
- **Framework**: FastAPI with Pydantic
- **AI Model**: IBM watsonx.ai Granite 3 8B Instruct
- **Deployment**: IBM Cloud Code Engine (containerized)

---
*Last Updated: 2026-01-31*
