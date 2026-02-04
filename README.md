# A.E.G.I.S. - Automated Escalation & Governance Intelligence System

**Confidence-Aware Agent Orchestration for Enterprise IT Operations**

Built for IBM watsonx Dev Day Hackathon 2026 | Team BlueShift

---

## The Problem

Modern enterprises face a critical challenge in IT operations: **agentic AI systems that act confidently even when they shouldn't**.

Current AI-driven automation systems have a dangerous blind spot:
- They execute remediation actions without recognizing their own uncertainty
- False positives lead to unnecessary service disruptions
- High-stakes decisions are made without human oversight
- There's no governance layer between AI confidence and automated execution

**The result?** Enterprises hesitate to fully adopt agentic AI for critical operations, missing out on efficiency gains while still bearing manual toil.

---

## Our Solution

**A.E.G.I.S.** is a confidence-aware multi-agent orchestration system that introduces a critical innovation: **AI that knows when NOT to act**.

### Core Innovation: Confidence-Based Routing

```
Incident Alert
     │
     ▼
┌─────────────────┐
│  Triage Agent   │ ─── Classifies incident, extracts context
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Decision Agent  │ ─── watsonx.ai Granite model analyzes
│   (watsonx.ai)  │     and returns CONFIDENCE SCORE
└────────┬────────┘
         │
         ▼
    ┌────┴────┐
    │  ≥80%?  │
    └────┬────┘
    YES  │  NO
    │    │
    ▼    ▼
┌──────┐ ┌──────────────┐
│ Auto │ │ Human-in-    │
│ Exec │ │ the-Loop     │
└──────┘ └──────────────┘
```

**The Confidence Threshold (80%):**
- **≥80% Confidence:** Clear incident with aligned signals → Auto-execute via MCP tools
- **<80% Confidence:** Ambiguous or conflicting signals → Escalate to human operator

This simple but powerful branching ensures AI automation only acts when appropriate, while unclear situations always get human oversight.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        watsonx Orchestrate                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Incident │→│ Decision │→│Governance│→│ Approval │→│Resolution│  │
│  │  Intake  │  │   Agent  │  │  Agent   │  │  Agent   │  │  Summary │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│       ↑              │              │             │             │       │
└───────┼──────────────┼──────────────┼─────────────┼─────────────┼───────┘
        │              │              │             │             │
        │              ▼              │             │             │
        │    ┌─────────────────┐      │             │             │
        │    │ aegis-decision  │      │             │             │
        │    │    -service     │      │             │             │
        │    │ (watsonx.ai)    │      │             │             │
        │    └─────────────────┘      │             │             │
        │                             ▼             ▼             │
        │                   ┌─────────────────────────┐           │
        │                   │      aegis-mcp          │           │
        │                   │   (MCP Tool Server)     │           │
        │                   │  ┌─────────────────┐    │           │
        │                   │  │ HashiCorp Vault │    │           │
        │                   │  │  (Secrets Mgmt) │    │           │
        │                   │  └─────────────────┘    │           │
        │                   └─────────────────────────┘           │
        │                                                         │
   ┌────┴─────────────────────────────────────────────────────────┴────┐
   │                          aegis-ui                                  │
   │              (Next.js Dashboard + Orchestrate Chat)                │
   └────────────────────────────────────────────────────────────────────┘
```

---

## Multi-Agent System

A.E.G.I.S. uses **5 specialized agents** working together within IBM watsonx Orchestrate:

| Agent | Role | Key Capability |
|-------|------|----------------|
| **Incident Intake Agent** | Receives alerts from monitoring systems (ServiceNow, PagerDuty, etc.) | Parses and normalizes incident data |
| **Decision & Confidence Agent** | Analyzes incident using watsonx.ai Granite | Returns confidence score + recommended action |
| **Orchestration & Governance Agent** | Routes based on confidence threshold | Enforces policy: ≥80% auto-exec, <80% escalate |
| **Human-in-the-Loop Agent** | Handles low-confidence escalations | Presents options, collects human decision |
| **Resolution Summary Agent** | Generates post-incident documentation | Creates audit trail and learns from outcomes |

### Agent Authorization ("Smart ID Badge")

Each agent carries a unique identifier used for authorization. The MCP server enforces capability-based access:

| Tool | Allowed Agents |
|------|----------------|
| `execute_runbook` | Execution Agent ONLY |
| `get_secret` | Execution Agent ONLY |
| `run_diagnostics` | Execution + Triage Agents |

This ensures only authorized agents can perform sensitive operations.

---

## Repository Structure

```
AEGIS/
├── aegis-decision-service/    # Python FastAPI service (watsonx.ai)
│   ├── src/aegis_service/
│   │   ├── main.py           # FastAPI endpoints
│   │   ├── watsonx_client.py # Granite LLM integration
│   │   └── models.py         # Pydantic schemas
│   ├── runbooks/             # Markdown runbook templates
│   ├── Dockerfile
│   └── requirements.txt
│
├── aegis-mcp/                 # MCP Tool Server
│   ├── app/
│   │   ├── main.py           # FastAPI + MCP protocol
│   │   ├── tools.py          # Tool implementations
│   │   ├── auth.py           # Bearer token auth
│   │   ├── policy.py         # Agent badge authorization
│   │   └── vault.py          # HashiCorp Vault integration
│   ├── Dockerfile
│   └── requirements.txt
│
└── aegis-ui/                  # Next.js Dashboard
    ├── app/
    │   └── page.tsx          # Main dashboard
    ├── components/
    │   └── OrchestrateChatEmbed.tsx  # Chat integration
    └── package.json
```

---

## Components

### 1. Decision Service (`aegis-decision-service`)

The brain of A.E.G.I.S. - uses IBM watsonx.ai with Granite 3 8B Instruct to analyze incidents.

**Key Features:**
- Ambiguity-aware confidence scoring
- Pattern detection for conflicting signals
- Policy enforcement (auto-caps ambiguous incidents at 60%)
- Runbook context injection for domain knowledge

**API Endpoints:**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/version` | GET | Service version and configuration |
| `/evaluate-incident` | POST | Analyze incident, return confidence + action |
| `/docs` | GET | Interactive API documentation |

**Example Request:**
```bash
curl -X POST https://your-service-url/evaluate-incident \
  -H "Content-Type: application/json" \
  -d '{
    "incident_text": "Disk space at 99% on Server-DB-01; /var/log growing rapidly.",
    "category": "storage"
  }'
```

**Example Response:**
```json
{
  "confidence_score": 95,
  "recommended_action": "clear_logs",
  "reasoning": "Clear disk space issue with identifiable cause...",
  "requires_approval": false,
  "runbook_reference": "storage-incident-runbook.md"
}
```

### 2. MCP Server (`aegis-mcp`)

Model Context Protocol server exposing diagnostic and execution tools.

**Available Tools:**
| Tool | Description | Auth Required |
|------|-------------|---------------|
| `get_secret` | Retrieve secrets from Vault | Execution Agent |
| `run_diagnostics` | Analyze incident patterns | Execution + Triage |
| `execute_runbook` | Execute remediation actions | Execution Agent |

**Security Features:**
- Two-layer auth: Bearer token + Agent ID
- HashiCorp Vault integration
- Audit-friendly response fields
- Simulated execution for safety

### 3. Operations Dashboard (`aegis-ui`)

Next.js dashboard for incident management and AEGIS interaction.

**Features:**
- Incident list with filtering and search
- Create incident form
- Embedded AEGIS chat (watsonx Orchestrate)
- Service uptime monitoring
- SLA compliance trends
- MTTR metrics visualization
- Triage outcome history

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- IBM Cloud account with watsonx.ai access
- (Optional) HashiCorp Vault for secrets management

### 1. Decision Service Setup

```bash
cd aegis-decision-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials:
#   WATSONX_APIKEY=your_api_key
#   WATSONX_PROJECT_ID=your_project_id
#   WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Run locally
uvicorn src.aegis_service.main:app --host 0.0.0.0 --port 5000 --reload
```

### 2. MCP Server Setup

```bash
cd aegis-mcp

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
export MCP_BEARER_TOKEN="$(python -c 'import secrets; print(secrets.token_hex(24))')"
export AEGIS_EXECUTION_AGENT_ID="your-agent-uuid"

# Run locally
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

### 3. UI Dashboard Setup

```bash
cd aegis-ui

# Install dependencies
pnpm install  # or npm install

# Run development server
pnpm dev  # or npm run dev

# Open http://localhost:3000
```

---

## Deployment

All components are designed for IBM Cloud Code Engine deployment.

### Environment Variables

**Decision Service:**
```
WATSONX_APIKEY=<your-ibm-cloud-api-key>
WATSONX_PROJECT_ID=<your-watsonx-project-id>
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-3-8b-instruct
PORT=5000
```

**MCP Server:**
```
MCP_BEARER_TOKEN=<secure-token>
AEGIS_EXECUTION_AGENT_ID=<agent-uuid>
VAULT_ADDR=<vault-url>  # Optional
VAULT_TOKEN=<vault-token>  # Optional
PORT=8080
```

### Deploy to Code Engine

```bash
# Login to IBM Cloud
ibmcloud login --apikey YOUR_API_KEY -r eu-gb

# Select Code Engine project
ibmcloud ce project select --name "your-project"

# Deploy Decision Service
ibmcloud ce app create \
  --name aegis-decision-service \
  --build-source ./aegis-decision-service \
  --port 5000 \
  --env WATSONX_APIKEY=xxx \
  --env WATSONX_PROJECT_ID=xxx \
  --wait

# Deploy MCP Server
ibmcloud ce app create \
  --name aegis-mcp \
  --build-source ./aegis-mcp \
  --port 8080 \
  --env MCP_BEARER_TOKEN=xxx \
  --wait
```

---

## Demo Scenarios

### Scenario 1: High Confidence (Auto-Execute)

**Input:** "Disk usage at 95%. Log rotation failed. No user impact."

**Result:**
- Confidence Score: **95%**
- Action: `clear_logs`
- Outcome: Automatic execution via MCP tools

### Scenario 2: Low Confidence (Human Escalation)

**Input:** "Database latency is high but system metrics look normal."

**Result:**
- Confidence Score: **50%** (capped due to conflicting signals)
- Action: `escalate_to_human`
- Outcome: Routed to human operator for decision

### Scenario 3: Ambiguous Pattern

**Input:** "Intermittent auth failures. No clear pattern. May be deployment related."

**Result:**
- Confidence Score: **40%**
- Action: `run_diagnostics`
- Outcome: Additional investigation before any action

---

## Key Differentiators

1. **Confidence-First Design:** Every decision includes uncertainty quantification
2. **Governance Built-In:** Policy enforcement at the orchestration layer
3. **Human-in-the-Loop:** Seamless escalation for ambiguous situations
4. **Audit Trail:** Complete traceability of agent decisions
5. **Safe Execution:** Simulated actions with real-world output format
6. **Enterprise-Ready:** Vault integration, RBAC, multi-agent authorization

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| LLM | IBM watsonx.ai (Granite 3 8B Instruct) |
| Orchestration | IBM watsonx Orchestrate |
| Backend | Python, FastAPI |
| Frontend | Next.js 14, React, Tailwind CSS |
| Secrets | HashiCorp Vault |
| Protocol | MCP (Model Context Protocol) |
| Deployment | IBM Cloud Code Engine |

---

## API Documentation

Each service exposes interactive API documentation:

- **Decision Service:** `https://your-decision-service-url/docs`
- **MCP Server:** `https://your-mcp-url/docs`

OpenAPI specifications can be exported for watsonx Orchestrate import.

---

## Security Considerations

- **Never commit credentials** - Use environment variables
- **Agent authorization** - MCP tools require valid agent IDs
- **Vault secrets** - Sensitive data never exposed to callers
- **Simulated execution** - Production safety during hackathon
- **Audit logging** - All tool calls are logged with authorization details

---

## Team BlueShift

Built for IBM watsonx Dev Day Hackathon 2026

---

## License

MIT

---

*"AI that knows when NOT to act" - Bringing governance to agentic AI*
