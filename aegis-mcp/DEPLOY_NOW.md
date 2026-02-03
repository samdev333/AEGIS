# AEGIS MCP Server - Code Engine Deployment Guide

Step-by-step guide to deploy to IBM Cloud Code Engine with agent authorization.

## Prerequisites

- IBM Cloud account
- IBM Cloud CLI installed (`ibmcloud`)
- Code Engine plugin installed (`ibmcloud plugin install code-engine`)
- Logged in: `ibmcloud login --sso`

## Required Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MCP_BEARER_TOKEN` | Yes | Bearer token for API auth |
| `AEGIS_EXECUTION_AGENT_ID` | Yes | Orchestrate Execution Agent ID |
| `AEGIS_TRIAGE_AGENT_ID` | No | Orchestrate Triage Agent ID |
| `AEGIS_EXEC_TOKEN` | No | Token returned by get_secret |
| `VAULT_ADDR` | No | HashiCorp Vault URL |
| `VAULT_TOKEN` | No | Vault authentication token |
| `VAULT_NAMESPACE` | No | Vault namespace (HCP Vault) |
| `VAULT_KV_MOUNT` | No | KV mount path (default: secret) |
| `VAULT_SECRET_PATH` | No | Secret path (default: aegis/mcp) |

## Option 1: CLI Deployment (Recommended)

### Step 1: Target Region and Create/Select Project

```bash
# Target the region (eu-gb for London, us-south for Dallas)
ibmcloud target -r eu-gb

# Create a new project (or select existing)
ibmcloud ce project create --name aegis-mcp-project

# Or select existing project
ibmcloud ce project select --name aegis-mcp-project
```

### Step 2: Create Secrets

```bash
# Create secret with all required env vars
ibmcloud ce secret create --name aegis-mcp-secrets \
  --from-literal MCP_BEARER_TOKEN=<your_bearer_token> \
  --from-literal AEGIS_EXECUTION_AGENT_ID=<your_agent_uuid> \
  --from-literal AEGIS_EXEC_TOKEN=<your_exec_token>
```

**With Vault integration:**

```bash
ibmcloud ce secret create --name aegis-mcp-secrets \
  --from-literal MCP_BEARER_TOKEN=<your_bearer_token> \
  --from-literal AEGIS_EXECUTION_AGENT_ID=<your_agent_uuid> \
  --from-literal AEGIS_EXEC_TOKEN=<your_exec_token> \
  --from-literal VAULT_ADDR=https://vault.example.com:8200 \
  --from-literal VAULT_TOKEN=<your_vault_token> \
  --from-literal VAULT_NAMESPACE=admin \
  --from-literal VAULT_KV_MOUNT=secret \
  --from-literal VAULT_SECRET_PATH=aegis/mcp
```

### Step 3: Build and Deploy (Source-to-Image)

```bash
# From the aegis-mcp directory
ibmcloud ce app create --name aegis-mcp-server \
  --build-source . \
  --strategy dockerfile \
  --env-from-secret aegis-mcp-secrets \
  --port 8080 \
  --min-scale 0 \
  --max-scale 3
```

### Step 4: Get Application URL

```bash
ibmcloud ce app get --name aegis-mcp-server --output url
```

### Step 5: Test Deployment

```bash
# Replace <APP_URL> with actual URL from previous step

# Health check
curl https://<APP_URL>/health

# Run diagnostics (with agent_id)
curl -X POST https://<APP_URL>/mcp/tools/run_diagnostics \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_bearer_token>" \
  -d '{
    "agent_id": "<your_agent_uuid>",
    "incident_text": "High memory usage on database server"
  }'

# Execute runbook (with agent_id)
curl -X POST https://<APP_URL>/mcp/tools/execute_runbook \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_bearer_token>" \
  -d '{
    "agent_id": "<your_agent_uuid>",
    "action": "restart_service",
    "parameters": {"service": "nginx"}
  }'

# Test MCP protocol
curl -X POST https://<APP_URL>/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{}}}'
```

## Option 2: Deploy from GitHub

### Step 1: Push Code to GitHub

```bash
git init
git add .
git commit -m "AEGIS MCP server with agent authorization"
git remote add origin https://github.com/YOUR_USERNAME/aegis-mcp.git
git push -u origin main
```

### Step 2: Deploy from GitHub via CLI

```bash
ibmcloud ce app create --name aegis-mcp-server \
  --build-source https://github.com/YOUR_USERNAME/aegis-mcp \
  --strategy dockerfile \
  --env-from-secret aegis-mcp-secrets \
  --port 8080
```

## Option 3: Web Console Deployment

1. Go to [IBM Cloud Code Engine Console](https://cloud.ibm.com/codeengine/overview)
2. Select or create a project
3. Click **Applications** > **Create**
4. Choose **Source code**
5. Enter GitHub repo URL or upload source
6. Set build strategy to **Dockerfile**
7. Under **Environment variables**, add:
   - `MCP_BEARER_TOKEN`: your bearer token
   - `AEGIS_EXECUTION_AGENT_ID`: your agent UUID from Orchestrate
   - `AEGIS_EXEC_TOKEN`: your execution token
   - (Optional) Vault variables if using Vault
8. Set port to `8080`
9. Click **Create**

## Updating Secrets

To update the Execution Agent ID or add new agents:

```bash
# Delete and recreate secrets
ibmcloud ce secret delete --name aegis-mcp-secrets --force

ibmcloud ce secret create --name aegis-mcp-secrets \
  --from-literal MCP_BEARER_TOKEN=<your_token> \
  --from-literal AEGIS_EXECUTION_AGENT_ID=<new_agent_uuid> \
  --from-literal AEGIS_TRIAGE_AGENT_ID=<triage_agent_uuid> \
  --from-literal AEGIS_EXEC_TOKEN=<your_exec_token>

# Restart app to pick up new secrets
ibmcloud ce app update --name aegis-mcp-server --env-from-secret aegis-mcp-secrets
```

## Updating the Application

After making code changes:

```bash
# Rebuild and redeploy
ibmcloud ce app update --name aegis-mcp-server --build-source .
```

## View Logs

```bash
# Stream logs
ibmcloud ce app logs --name aegis-mcp-server --follow

# View recent logs
ibmcloud ce app logs --name aegis-mcp-server
```

## Troubleshooting

### 403 Forbidden - Agent Not Authorized

If you get `Agent 'xxx' is not authorized for capability 'yyy'`:

1. Verify `AEGIS_EXECUTION_AGENT_ID` is set correctly in secrets
2. Check the agent_id in your request matches exactly
3. For `execute_runbook` and `get_secret`, only Execution Agent is allowed

```bash
# Check secret values
ibmcloud ce secret get --name aegis-mcp-secrets
```

### 400 Bad Request - Missing agent_id

All tool endpoints now require `agent_id` in the request body:

```json
{
  "agent_id": "<your_agent_uuid>",
  "incident_text": "..."
}
```

### Vault Secret Not Loading

If `vault_secret_loaded: false` in responses:

1. Check VAULT_ADDR and VAULT_TOKEN are set
2. Verify the secret exists at the correct path
3. Check Vault token has read permissions

```bash
# Test Vault connection locally
curl -H "X-Vault-Token: $VAULT_TOKEN" $VAULT_ADDR/v1/secret/data/aegis/mcp
```

### Container Registry Permission Errors

**Solution 1: Use Source-to-Image (Recommended)**
```bash
ibmcloud ce app create --name aegis-mcp-server --build-source .
```

**Solution 2: Create Container Registry Namespace**
```bash
ibmcloud plugin install container-registry
ibmcloud cr namespace-add aegis-namespace
ibmcloud cr login

docker build -t <region>.icr.io/aegis-namespace/aegis-mcp:latest .
docker push <region>.icr.io/aegis-namespace/aegis-mcp:latest

ibmcloud ce app create --name aegis-mcp-server \
  --image <region>.icr.io/aegis-namespace/aegis-mcp:latest \
  --env-from-secret aegis-mcp-secrets
```

### Application Not Starting

```bash
# Check application status
ibmcloud ce app get --name aegis-mcp-server

# Check build logs
ibmcloud ce buildrun list
ibmcloud ce buildrun logs --name <buildrun-name>

# Check application events
ibmcloud ce app events --name aegis-mcp-server
```

### Cold Start Delays

To keep at least one instance running:
```bash
ibmcloud ce app update --name aegis-mcp-server --min-scale 1
```

## Cleanup

```bash
# Delete application
ibmcloud ce app delete --name aegis-mcp-server --force

# Delete secrets
ibmcloud ce secret delete --name aegis-mcp-secrets --force

# Delete project (removes everything)
ibmcloud ce project delete --name aegis-mcp-project --force
```

## Quick Reference

| Command | Description |
|---------|-------------|
| `ibmcloud ce app list` | List all applications |
| `ibmcloud ce app get -n aegis-mcp-server` | Get app details |
| `ibmcloud ce app logs -n aegis-mcp-server -f` | Stream logs |
| `ibmcloud ce app update -n aegis-mcp-server --build-source .` | Redeploy |
| `ibmcloud ce secret list` | List secrets |
| `ibmcloud ce secret get -n aegis-mcp-secrets` | View secret keys |
