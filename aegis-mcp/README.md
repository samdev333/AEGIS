# AEGIS MCP Server

MCP (Model Context Protocol) server exposing diagnostic and execution tools for IT incident analysis. Features **agent-based authorization** using Orchestrate Agent IDs ("Smart ID Badge") and optional HashiCorp Vault integration.

## Features

- **get_secret**: Retrieve secrets (Execution Agent only)
- **run_diagnostics**: Analyze incident text (Execution + Triage agents)
- **execute_runbook**: Execute simulated runbook actions (Execution Agent only)
- Two-layer authentication: Bearer token + Agent ID authorization
- HashiCorp Vault integration for secret verification
- Audit-friendly response fields for compliance
- MCP protocol support (SSE and Streamable HTTP transports)

## Authorization Model ("Smart ID Badge")

Each tool call requires an `agent_id` in the request body. The server enforces:

| Capability | Allowed Agents |
|------------|----------------|
| `execute_runbook` | Execution Agent ONLY |
| `get_secret` | Execution Agent ONLY |
| `run_diagnostics` | Execution Agent + Triage Agent |

Authorization order:
1. Bearer token verification (401 if invalid)
2. Agent ID validation (400 if missing)
3. Agent allowlist check (403 if not authorized)
4. Vault secret load (graceful degradation if unavailable)

## API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/health` | GET | No | Health check |
| `/mcp/tools/get_secret` | POST | Bearer + Agent | Retrieve a secret |
| `/mcp/tools/run_diagnostics` | POST | Bearer + Agent | Run incident diagnostics |
| `/mcp/tools/execute_runbook` | POST | Bearer + Agent | Execute runbook (simulated) |
| `/` or `/mcp` | POST | No | MCP JSON-RPC endpoint |
| `/` or `/sse` | GET | No | MCP SSE endpoint |

## Local Development

### 1. Create Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables

```bash
# Windows (PowerShell)
$env:MCP_BEARER_TOKEN="<your_bearer_token>"
$env:AEGIS_EXECUTION_AGENT_ID="<your_agent_uuid>"
$env:AEGIS_EXEC_TOKEN="<your_exec_token>"
$env:PORT="8080"

# Linux/macOS
export MCP_BEARER_TOKEN="<your_bearer_token>"
export AEGIS_EXECUTION_AGENT_ID="<your_agent_uuid>"
export AEGIS_EXEC_TOKEN="<your_exec_token>"
export PORT=8080
```

> **TIP**: Generate a bearer token with: `python -c "import secrets; print('aegis_mcp_' + secrets.token_hex(24))"`

> **WARNING**: Never commit real tokens to version control.

### 4. Run the Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

## Testing with cURL

### Health Check (no auth)

```bash
curl http://localhost:8080/health
```

### Authorized Request (correct agent_id)

```bash
curl -X POST http://localhost:8080/mcp/tools/run_diagnostics \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_bearer_token>" \
  -d '{
    "agent_id": "<your_agent_uuid>",
    "incident_text": "High CPU usage on production server"
  }'
```

### Missing agent_id (400 Bad Request)

```bash
curl -X POST http://localhost:8080/mcp/tools/run_diagnostics \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_bearer_token>" \
  -d '{"incident_text": "High CPU"}'
```

### Unauthorized agent_id (403 Forbidden)

```bash
curl -X POST http://localhost:8080/mcp/tools/execute_runbook \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_bearer_token>" \
  -d '{
    "agent_id": "wrong-agent-id-12345",
    "action": "restart_service",
    "parameters": {"service": "nginx"}
  }'
```

### Execute Runbook (Execution Agent only)

```bash
curl -X POST http://localhost:8080/mcp/tools/execute_runbook \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_bearer_token>" \
  -d '{
    "agent_id": "<your_agent_uuid>",
    "action": "clear_logs",
    "parameters": {"retention_days": 7}
  }'
```

### Test MCP Protocol

```bash
# Initialize
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{}}}'

# List tools
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'

# Call tool
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"run_diagnostics","arguments":{"agent_id":"<your_agent_uuid>","incident_text":"High CPU"}}}'
```

## Response Format

All tool responses include audit-friendly authorization info:

```json
{
  "authorization": {
    "authorized_agent_id": "<agent_uuid>",
    "authorization_check": "passed",
    "policy": "run_diagnostics",
    "vault_secret_loaded": true,
    "mutating_actions_taken": false
  },
  "safety": {
    "mutating_actions_taken": false,
    "notes": "..."
  }
}
```

## Orchestrate Integration

When configuring your Orchestrate agent to call this MCP server:

1. **Add MCP Server**: Use the base URL of your deployed server
2. **Transport**: Streamable HTTP or SSE
3. **Tool Parameters**: The `agent_id` field is included in each tool's input schema
4. **Agent Instructions**: Add to your agent's guidelines:

```
When calling any MCP tool (run_diagnostics, execute_runbook, get_secret),
you MUST always include your agent_id parameter with your Agent ID.
This is your identity badge for authorization.
```

## Vault Integration (Optional)

To enable Vault secret verification:

```bash
export VAULT_ADDR="https://vault.example.com:8200"
export VAULT_TOKEN="<your_vault_token>"
export VAULT_NAMESPACE="admin"  # if using HCP Vault
export VAULT_KV_MOUNT="secret"
export VAULT_SECRET_PATH="aegis/mcp"
```

The server will attempt to read from `secret/data/aegis/mcp` and report `vault_secret_loaded: true/false` in responses. The actual secret value is never returned to callers.

## Export OpenAPI Schema

```bash
python scripts/export_openapi.py
```

## Docker

```bash
docker build -t aegis-mcp:latest .

docker run -p 8080:8080 \
  -e MCP_BEARER_TOKEN="<your_bearer_token>" \
  -e AEGIS_EXECUTION_AGENT_ID="<your_agent_uuid>" \
  aegis-mcp:latest
```

## Deployment

See [DEPLOY_NOW.md](DEPLOY_NOW.md) for IBM Cloud Code Engine deployment instructions.

## Project Structure

```
aegis-mcp/
├── app/
│   ├── __init__.py      # Package init
│   ├── main.py          # FastAPI application
│   ├── auth.py          # Bearer token authentication
│   ├── policy.py        # Agent badge authorization
│   ├── vault.py         # HashiCorp Vault integration
│   ├── mcp_protocol.py  # MCP JSON-RPC protocol handler
│   └── tools.py         # Tool implementations
├── scripts/
│   └── export_openapi.py
├── Dockerfile
├── requirements.txt
├── README.md
├── DEPLOY_NOW.md
├── .gitignore
└── .env.example
```

## Security Notes

- Store tokens in Code Engine secrets, not environment variables
- Agent IDs act as a second authorization layer ("Smart ID Badge")
- Vault secrets are verified but never returned to callers
- All runbook executions are SIMULATED for hackathon safety
- Never commit `.env` files with real credentials

## License

MIT
