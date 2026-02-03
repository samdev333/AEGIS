"""AEGIS MCP Server - Main FastAPI application with agent authorization and MCP protocol."""
import os
import json
import asyncio
from typing import Any
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

from app.auth import security, verify_token
from app.policy import Capability, authorize, get_authorization_info
from app.vault import load_vault_token
from app.tools import get_secret, run_diagnostics, execute_runbook
from app.mcp_protocol import (
    process_jsonrpc_message,
    MCP_TOOLS,
    SERVER_INFO,
    SERVER_CAPABILITIES,
    MCP_VERSION,
)

app = FastAPI(
    title="AEGIS MCP Server",
    description="MCP server exposing diagnostic and execution tools for IT incident analysis. "
                "Enforces agent-based authorization using Orchestrate Agent IDs.",
    version="0.2.0",
)


# =============================================================================
# Request Models (with agent_id)
# =============================================================================

class GetSecretRequest(BaseModel):
    agent_id: str = Field(..., description="Orchestrate Agent ID (UUID) making this request")
    name: str = Field(..., description="Name of the secret to retrieve")


class RunDiagnosticsRequest(BaseModel):
    agent_id: str = Field(..., description="Orchestrate Agent ID (UUID) making this request")
    incident_text: str = Field(..., description="Description of the incident to diagnose")


class ExecuteRunbookRequest(BaseModel):
    agent_id: str = Field(..., description="Orchestrate Agent ID (UUID) making this request")
    action: str = Field(..., description="Runbook action: clear_logs, restart_service, run_diagnostics")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Action-specific parameters")


# =============================================================================
# Response Models (with audit fields)
# =============================================================================

class HealthResponse(BaseModel):
    status: str


class AuthorizationInfo(BaseModel):
    authorized_agent_id: str
    authorization_check: str
    policy: str
    vault_secret_loaded: bool
    mutating_actions_taken: bool = False


class GetSecretResponse(BaseModel):
    name: str
    value: str
    authorization: AuthorizationInfo


class DiagnosticsOutput(BaseModel):
    likely_causes: list[str]
    recommended_next_steps: list[str]
    signals_to_check: list[str]
    sample_queries: list[str]


class SafetyInfo(BaseModel):
    mutating_actions_taken: bool
    notes: str


class RunDiagnosticsResponse(BaseModel):
    incident: str
    diagnostics: DiagnosticsOutput
    safety: SafetyInfo
    authorization: AuthorizationInfo


class RunbookDetails(BaseModel):
    action: str
    status: str
    details: dict[str, Any]
    execution_log: list[str]


class ExecuteRunbookResponse(BaseModel):
    runbook: RunbookDetails
    safety: SafetyInfo
    authorization: AuthorizationInfo


# =============================================================================
# Helper: Authorization flow
# =============================================================================

def enforce_authorization(agent_id: str, capability: Capability) -> dict:
    """
    Enforce agent authorization and attempt Vault secret load.
    """
    try:
        validated_agent_id = authorize(agent_id, capability)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    auth_info = get_authorization_info(validated_agent_id, capability)
    vault_result = load_vault_token()
    auth_info["vault_secret_loaded"] = vault_result.get("vault_secret_loaded", False)
    auth_info["mutating_actions_taken"] = False

    return auth_info


# =============================================================================
# MCP Protocol Endpoints (SSE Transport)
# =============================================================================

@app.get("/", tags=["MCP Protocol"])
@app.get("/sse", tags=["MCP Protocol"])
async def mcp_sse_endpoint(request: Request):
    """
    MCP Server-Sent Events endpoint for Orchestrate integration.
    Handles the MCP protocol over SSE transport.
    """
    async def event_generator():
        # Send initial endpoint info
        endpoint_msg = {
            "type": "endpoint",
            "url": "/messages"
        }
        yield f"data: {json.dumps(endpoint_msg)}\n\n"

        # Keep connection alive
        while True:
            if await request.is_disconnected():
                break
            # Send keepalive ping every 30 seconds
            yield ": keepalive\n\n"
            await asyncio.sleep(30)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@app.post("/messages", tags=["MCP Protocol"])
async def mcp_messages_endpoint(request: Request):
    """
    MCP JSON-RPC message handler endpoint.
    Processes MCP protocol messages (initialize, tools/list, tools/call).
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None}
        )

    response = process_jsonrpc_message(body)

    if response is None:
        # Notification - no response needed
        return JSONResponse(status_code=204, content=None)

    return JSONResponse(content=response)


@app.post("/", tags=["MCP Protocol"])
@app.post("/mcp", tags=["MCP Protocol"])
async def mcp_streamable_http(request: Request):
    """
    MCP Streamable HTTP endpoint (alternative to SSE).
    Handles MCP protocol over standard HTTP POST.
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None}
        )

    response = process_jsonrpc_message(body)

    if response is None:
        return JSONResponse(status_code=204, content=None)

    return JSONResponse(content=response)


# =============================================================================
# REST API Endpoints (original)
# =============================================================================

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint - no authentication required."""
    return {"status": "ok"}


@app.post(
    "/mcp/tools/get_secret",
    response_model=GetSecretResponse,
    tags=["MCP Tools"],
    responses={
        400: {"description": "Missing or empty agent_id"},
        401: {"description": "Invalid Bearer token"},
        403: {"description": "Agent not authorized for this capability"},
    },
)
async def mcp_get_secret(
    request: GetSecretRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Retrieve a secret value by name."""
    await verify_token(credentials)
    auth_info = enforce_authorization(request.agent_id, Capability.GET_SECRET)
    result = get_secret(request.name)

    return {
        "name": result["name"],
        "value": result["value"],
        "authorization": auth_info,
    }


@app.post(
    "/mcp/tools/run_diagnostics",
    response_model=RunDiagnosticsResponse,
    tags=["MCP Tools"],
    responses={
        400: {"description": "Missing or empty agent_id"},
        401: {"description": "Invalid Bearer token"},
        403: {"description": "Agent not authorized for this capability"},
    },
)
async def mcp_run_diagnostics(
    request: RunDiagnosticsRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Run diagnostics on an incident description."""
    await verify_token(credentials)
    auth_info = enforce_authorization(request.agent_id, Capability.RUN_DIAGNOSTICS)
    result = run_diagnostics(request.incident_text)

    return {
        "incident": result["incident"],
        "diagnostics": result["diagnostics"],
        "safety": {
            "mutating_actions_taken": False,
            "notes": "Diagnostic analysis only - no changes made to systems",
        },
        "authorization": auth_info,
    }


@app.post(
    "/mcp/tools/execute_runbook",
    response_model=ExecuteRunbookResponse,
    tags=["MCP Tools"],
    responses={
        400: {"description": "Missing or empty agent_id"},
        401: {"description": "Invalid Bearer token"},
        403: {"description": "Agent not authorized for this capability"},
    },
)
async def mcp_execute_runbook(
    request: ExecuteRunbookRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Execute a runbook action (SIMULATED for hackathon)."""
    await verify_token(credentials)
    auth_info = enforce_authorization(request.agent_id, Capability.EXECUTE_RUNBOOK)
    result = execute_runbook(request.action, request.parameters)

    return {
        "runbook": {
            "action": result["action"],
            "status": result["status"],
            "details": result["details"],
            "execution_log": result["execution_log"],
        },
        "safety": {
            "mutating_actions_taken": False,
            "notes": "SIMULATED execution - no real changes made (hackathon mode)",
        },
        "authorization": auth_info,
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
