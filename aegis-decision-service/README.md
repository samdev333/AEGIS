# 🛡️ A.E.G.I.S. Decision Service v2.0

**Automated Escalation & Governance Intelligence System**

> Enterprise-grade AI agents that know when NOT to act

Built with **FastAPI**, **IBM watsonx.ai (Granite)**, and designed for **watsonx Orchestrate** integration.

---

## 🎯 What This Demonstrates

**The Critical Enterprise AI Pattern:**

> "AI systems that calculate confidence, respect uncertainty, and defer to humans when risk is high."

A.E.G.I.S. is a decision service that:
- Analyzes incidents using IBM watsonx.ai Granite models
- Calculates confidence scores based on context and runbook alignment
- Routes decisions automatically:
  - **Confidence ≥ 80**: Auto-execute standard remediation
  - **Confidence < 80**: Escalate to human with full context

**This is not automation. This is governed agentic AI.**

---

## 🏗️ Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────┐
│                 watsonx Orchestrate                     │
│                  (Control Plane)                        │
│                                                         │
│  ┌──────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │Intake│→ │ Decision │→ │Confidence│→ │Auto/Human │  │
│  │Agent │  │  Agent   │  │ Branch   │  │   Path    │  │
│  └──────┘  └────┬─────┘  └──────────┘  └───────────┘  │
└──────────────────│────────────────────────────────────────┘
                   │ HTTP POST /evaluate-incident
                   ▼
┌─────────────────────────────────────────────────────────┐
│           A.E.G.I.S. Decision Service (FastAPI)         │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ main.py (FastAPI App)                          │   │
│  │  • Request validation (Pydantic)                │   │
│  │  • Coordination & logging                       │   │
│  │  • Response construction                        │   │
│  └─────────┬──────────────────────┬────────────────┘   │
│            │                      │                     │
│            ▼                      ▼                     │
│  ┌──────────────────┐   ┌──────────────────┐          │
│  │runbook_context.py│   │watsonx_client.py │          │
│  │                  │   │                  │          │
│  │ • Local runbooks │   │ • Granite LLM    │          │
│  │ • Langflow hook  │   │ • JSON parsing   │          │
│  │ • Context format │   │ • Policy enforce │          │
│  └──────────────────┘   └────────┬─────────┘          │
│                                  │                     │
│                                  ▼                     │
│                         ┌─────────────────┐            │
│                         │ IBM watsonx.ai  │            │
│                         │ Granite 3 8B    │            │
│                         └─────────────────┘            │
└─────────────────────────────────────────────────────────┘
```

### Module Responsibilities

| Module | Responsibility |
|--------|---------------|
| **main.py** | FastAPI application, request coordination, error handling, logging |
| **models.py** | Pydantic models for strict JSON contracts |
| **watsonx_client.py** | watsonx.ai integration, robust JSON parsing, policy enforcement |
| **runbook_context.py** | Local runbook loading, optional Langflow integration |
| **runbooks/*.md** | Domain-specific incident runbooks (latency, storage, auth, unknown) |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- IBM Cloud account
- watsonx.ai project with Granite model access

### Step 1: Get IBM Cloud Credentials

#### API Key
```bash
# Go to: https://cloud.ibm.com
# Navigate to: Manage > Access (IAM) > API Keys
# Create key: "aegis-key"
# Copy immediately (won't be shown again)
```

#### Project ID
```bash
# Go to: https://dataplatform.cloud.ibm.com/wx/home
# Navigate to: Projects > Your Project > Manage tab
# Copy: Project ID
```

### Step 2: Local Setup

```bash
# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template .env
# Edit .env with your credentials
```

### Step 3: Configure Environment

Create `.env` file:

```bash
# Required
WATSONX_APIKEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here

# Optional
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-3-8b-instruct
PORT=5000

# Optional Langflow integration
# LANGFLOW_RUNBOOK_URL=https://your-langflow-endpoint.com/api/runbook
```

### Step 4: Run Locally

```bash
# Start the service
uvicorn src.aegis_service.main:app --reload --port 5000

# Or use the Python entry point
python src/aegis_service/main.py
```

Service will be available at: `http://localhost:5000`

### Step 5: Test

#### Health Check
```bash
curl http://localhost:5000/health
```

#### Evaluate Incident (High Confidence)
```bash
curl -X POST http://localhost:5000/evaluate-incident \
  -H "Content-Type: application/json" \
  -d '{
    "incident_text": "Disk usage at 95%. Log rotation service failed at 3 AM. No user impact. Standard log cleanup applies.",
    "category": "storage"
  }'
```

**Expected Response:**
```json
{
  "analysis": "Disk space critically low due to failed log rotation",
  "recommended_action": "clear_logs",
  "confidence_score": 95,
  "explanation": "Clear cause with standard remediation. Safe to auto-execute.",
  "runbook_context": "...",
  "trace_id": "uuid",
  "model_id": "ibm/granite-3-8b-instruct",
  "policy": {
    "auto_execute_threshold": 80,
    "escalate_threshold": 80
  }
}
```

#### Evaluate Incident (Low Confidence - Escalate)
```bash
curl -X POST http://localhost:5000/evaluate-incident \
  -H "Content-Type: application/json" \
  -d '{
    "incident_text": "Intermittent authentication failures reported by users. No clear pattern. May be related to deployment 2 hours ago.",
    "category": "auth"
  }'
```

**Expected Response:**
```json
{
  "analysis": "Authentication failures with unclear root cause",
  "recommended_action": "escalate_to_human",
  "confidence_score": 45,
  "explanation": "Intermittent failures require human investigation.",
  ...
}
```

---

## 📊 API Reference

### Endpoints

#### `GET /`
Root endpoint with service info

#### `GET /health`
Health check

**Response:**
```json
{"status": "ok"}
```

#### `GET /version`
Version and configuration info

**Response:**
```json
{
  "service": "A.E.G.I.S. Decision Service",
  "version": "2.0.0",
  "model_id": "ibm/granite-3-8b-instruct",
  "watsonx_url": "https://us-south.ml.cloud.ibm.com"
}
```

#### `POST /evaluate-incident`
**Main decision endpoint**

**Request Body:**
```json
{
  "incident_text": "string (required, min 10 chars)",
  "category": "latency|storage|auth|unknown (optional)",
  "reporter_role": "SRE|Developer|Manager|Other (optional)",
  "context": {} // optional additional fields
}
```

**Response:**
```json
{
  "analysis": "one-sentence summary",
  "recommended_action": "clear_logs|restart_service|run_diagnostics|escalate_to_human",
  "confidence_score": 0-100,
  "explanation": "brief explanation",
  "runbook_context": "relevant runbook excerpt",
  "trace_id": "unique-uuid",
  "model_id": "ibm/granite-3-8b-instruct",
  "policy": {
    "auto_execute_threshold": 80,
    "escalate_threshold": 80
  }
}
```

**Key Field: `confidence_score`**
- **≥ 80**: High confidence → safe for auto-execution
- **< 80**: Low confidence → must escalate to human

**This field enables conditional branching in watsonx Orchestrate.**

#### `GET /docs`
Interactive API documentation (Swagger UI)

#### `GET /openapi.json`
OpenAPI specification in JSON format

---

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_contract.py::test_confidence_policy_enforcement_low_confidence_wrong_action
```

### Test Coverage

Tests validate:
- ✅ Response schema compliance
- ✅ Confidence policy enforcement
- ✅ Fallback behavior on errors
- ✅ All incident categories
- ✅ Trace ID uniqueness
- ✅ Input validation
- ✅ OpenAPI schema generation

---

## ☁️ Deployment

### IBM Code Engine (Recommended)

#### Option A: Via Console

1. Go to [IBM Cloud Console](https://cloud.ibm.com)
2. Search **Code Engine**
3. **Create Project**: `aegis-project`
4. **Create Application**:
   - Name: `aegis-decision-service`
   - Source: Upload this directory
   - Port: `5000`
   - Environment Variables:
     - `WATSONX_APIKEY`
     - `WATSONX_PROJECT_ID`
     - `PORT=5000`
5. Deploy

You'll get a URL like:
```
https://aegis-decision-service.xxx.us-south.codeengine.appdomain.cloud
```

#### Option B: Via Dockerfile

```bash
# Build
docker build -t aegis-decision-service .

# Run locally
docker run -p 5000:5000 \
  -e WATSONX_APIKEY=your_key \
  -e WATSONX_PROJECT_ID=your_project_id \
  aegis-decision-service

# Push to IBM Container Registry and deploy to Code Engine
# (see IBM Code Engine docs for details)
```

### Export OpenAPI Spec

After deploying, update and export the OpenAPI spec:

```bash
# Export OpenAPI spec
python scripts/export_openapi.py

# This creates:
# - openapi.yaml (for watsonx Orchestrate)
# - openapi.json (for reference)

# Update the 'servers' section in openapi.yaml with your Code Engine URL
```

---

## 🔗 watsonx Orchestrate Integration

### Step 1: Update OpenAPI Spec

```yaml
# In openapi.yaml, update:
servers:
  - url: https://your-actual-code-engine-url.us-south.codeengine.appdomain.cloud
    description: Production Deployment
```

### Step 2: Import into Orchestrate

1. Go to watsonx Orchestrate
2. **Skills** > **Add Skill** > **Import OpenAPI**
3. Upload `openapi.yaml`
4. Test the "Evaluate Incident" skill

### Step 3: Build Workflow

See [docs/orchestrate-setup-guide.md](docs/orchestrate-setup-guide.md) for complete instructions on:
- Creating the orchestration flow
- Setting up confidence-based branching
- Implementing human-in-the-loop escalation

---

## 🎬 Demo Scenarios

See [docs/demo-scenarios.md](docs/demo-scenarios.md) for complete presentation scripts.

### Scenario A: High Confidence (Auto-Execute)
- **Incident**: Disk space critical, log rotation failed
- **Confidence**: 95
- **Action**: clear_logs (auto-executed)
- **Demo Point**: Efficiency

### Scenario B: Low Confidence (Escalate) ⭐
- **Incident**: Intermittent auth failures, unclear cause
- **Confidence**: 45
- **Action**: escalate_to_human (workflow pauses)
- **Demo Point**: **Governance - AI knows when NOT to act**

---

## 📁 Project Structure

```
aegis-agent/
├── src/
│   └── aegis_service/
│       ├── __init__.py
│       ├── main.py              # FastAPI application
│       ├── models.py            # Pydantic models (strict contracts)
│       ├── watsonx_client.py    # watsonx.ai integration
│       └── runbook_context.py   # Runbook retrieval (local + Langflow)
├── runbooks/
│   ├── latency.md               # Latency incident runbook
│   ├── storage.md               # Storage incident runbook
│   ├── auth.md                  # Authentication incident runbook
│   └── unknown.md               # General incident runbook
├── scripts/
│   └── export_openapi.py        # OpenAPI spec generator
├── tests/
│   ├── __init__.py
│   └── test_contract.py         # Contract validation tests
├── docs/
│   ├── demo-scenarios.md        # Presentation scripts
│   └── orchestrate-setup-guide.md  # Orchestrate integration guide
├── .env.template                # Environment template
├── .gitignore
├── Dockerfile                   # Production container
├── .dockerignore
├── Procfile                     # Code Engine deployment
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Test configuration
└── README.md                    # This file
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `WATSONX_APIKEY` | ✅ | - | IBM Cloud API key |
| `WATSONX_PROJECT_ID` | ✅ | - | watsonx.ai project ID |
| `WATSONX_URL` | ❌ | us-south | watsonx.ai region URL |
| `WATSONX_MODEL_ID` | ❌ | granite-3-8b-instruct | Model to use |
| `PORT` | ❌ | 5000 | Service port |
| `LANGFLOW_RUNBOOK_URL` | ❌ | - | Optional Langflow endpoint |

### Runbook Context

**Local (Default):**
- Runbooks are markdown files in `runbooks/`
- Organized by category: latency, storage, auth, unknown
- Always available, no external dependencies

**Langflow (Optional):**
- Set `LANGFLOW_RUNBOOK_URL` environment variable
- Service will POST to Langflow with: `{category, incident_text}`
- Expects response: `{context: "..."}`
- Falls back to local runbooks if Langflow unavailable

---

## 🏆 Hackathon Talking Points

### For Judges

**One-Liner:**
> "A.E.G.I.S. demonstrates how enterprises can safely deploy agentic AI by combining watsonx Orchestrate for workflow control, watsonx.ai for intelligent decisions, and confidence-based routing for human-in-the-loop governance."

**Key Points:**

1. **Real AI Reasoning** (not if-else)
   - Uses IBM Granite models for actual incident analysis
   - Confidence calculation based on context + runbook alignment

2. **watsonx Orchestrate as Control Plane**
   - Orchestrate owns workflow state and branching
   - Decision Service provides intelligence
   - Clean separation of concerns

3. **The Winning Pattern: "Knowing When NOT to Act"**
   - Low confidence automatically escalates
   - Human sees AI analysis before approving
   - Audit trail of all decisions

4. **Production-Ready Architecture**
   - Modular, testable, documented
   - Robust error handling with safe fallbacks
   - Strict JSON contracts for reliability
   - Structured logging with trace IDs

### Common Questions

**Q: How is this different from automation?**
> "Traditional automation is binary. A.E.G.I.S. calculates confidence and routes accordingly. The system recognizes ambiguity and escalates when uncertain."

**Q: What about false positives?**
> "Confidence thresholds are tunable. Conservative orgs can set higher thresholds. All decisions are logged and auditable in Orchestrate."

**Q: How does Langflow fit in?**
> "In this POC, runbook context is local markdown files. In production, we'd integrate Langflow for vector-based retrieval of historical patterns. The hook is already there via `LANGFLOW_RUNBOOK_URL`."

---

## 🎓 Learn More

- [IBM watsonx.ai Documentation](https://www.ibm.com/products/watsonx-ai)
- [watsonx Orchestrate Documentation](https://www.ibm.com/products/watsonx-orchestrate)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [IBM Granite Models](https://www.ibm.com/granite)

---

## 📝 Important Notes

### Hackathon POC Notice

**This is a proof-of-concept demonstration for the IBM Dev Day Hackathon.**

- Runbooks are synthetic examples (not real production runbooks)
- No PII or sensitive data
- No persistent storage
- Designed to demonstrate the governed agentic AI pattern

### Security

- Never commit `.env` files with real credentials
- API keys should be rotated after hackathon
- For production: implement proper secret management
- CORS is wide open for demo; restrict in production

---

## 🙋 Support

For hackathon questions:
- Check `/docs` endpoint for interactive API documentation
- Review [docs/demo-scenarios.md](docs/demo-scenarios.md) for presentation
- See [docs/orchestrate-setup-guide.md](docs/orchestrate-setup-guide.md) for integration

---

**Built for IBM Dev Day Hackathon 2026**

**Demonstrating Enterprise-Safe Agentic AI with watsonx**

*"AI that knows when NOT to act"*
