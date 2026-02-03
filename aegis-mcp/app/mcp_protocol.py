"""MCP Protocol implementation for Watson Orchestrate compatibility."""
import json
import uuid
from typing import Any, AsyncGenerator
from datetime import datetime, timezone

from app.tools import run_diagnostics, execute_runbook, get_secret
from app.policy import Capability, authorize, get_authorization_info
from app.vault import load_vault_token


# MCP Protocol version
MCP_VERSION = "2024-11-05"

# Tool definitions for MCP
MCP_TOOLS = [
    {
        "name": "run_diagnostics",
        "description": "Analyze an IT incident and return diagnostic information including likely causes, recommended steps, and signals to check.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent_id": {
                    "type": "string",
                    "description": "Orchestrate Agent ID (UUID) for authorization"
                },
                "incident_text": {
                    "type": "string",
                    "description": "Description of the incident to diagnose"
                }
            },
            "required": ["agent_id", "incident_text"]
        }
    },
    {
        "name": "execute_runbook",
        "description": "Execute a runbook action (simulated). Supported actions: clear_logs, restart_service, run_diagnostics.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent_id": {
                    "type": "string",
                    "description": "Orchestrate Agent ID (UUID) for authorization"
                },
                "action": {
                    "type": "string",
                    "enum": ["clear_logs", "restart_service", "run_diagnostics"],
                    "description": "The runbook action to execute"
                },
                "parameters": {
                    "type": "object",
                    "description": "Action-specific parameters",
                    "additionalProperties": True
                }
            },
            "required": ["agent_id", "action"]
        }
    },
    {
        "name": "get_secret",
        "description": "Retrieve a secret value by name. Currently supports 'execution_token'.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent_id": {
                    "type": "string",
                    "description": "Orchestrate Agent ID (UUID) for authorization"
                },
                "name": {
                    "type": "string",
                    "description": "Name of the secret to retrieve"
                }
            },
            "required": ["agent_id", "name"]
        }
    }
]

# Server capabilities
SERVER_CAPABILITIES = {
    "tools": {
        "listChanged": False
    }
}

SERVER_INFO = {
    "name": "aegis-mcp-server",
    "version": "0.2.0"
}


def create_jsonrpc_response(id: Any, result: Any) -> dict:
    """Create a JSON-RPC 2.0 response."""
    return {
        "jsonrpc": "2.0",
        "id": id,
        "result": result
    }


def create_jsonrpc_error(id: Any, code: int, message: str, data: Any = None) -> dict:
    """Create a JSON-RPC 2.0 error response."""
    error = {
        "code": code,
        "message": message
    }
    if data is not None:
        error["data"] = data
    return {
        "jsonrpc": "2.0",
        "id": id,
        "error": error
    }


def handle_initialize(params: dict) -> dict:
    """Handle MCP initialize request."""
    return {
        "protocolVersion": MCP_VERSION,
        "capabilities": SERVER_CAPABILITIES,
        "serverInfo": SERVER_INFO
    }


def handle_tools_list(params: dict) -> dict:
    """Handle tools/list request."""
    return {
        "tools": MCP_TOOLS
    }


def handle_tools_call(params: dict) -> dict:
    """Handle tools/call request."""
    tool_name = params.get("name")
    arguments = params.get("arguments", {})

    # Get agent_id from arguments
    agent_id = arguments.get("agent_id")

    try:
        if tool_name == "run_diagnostics":
            # Authorize
            capability = Capability.RUN_DIAGNOSTICS
            validated_agent = authorize(agent_id, capability)
            auth_info = get_authorization_info(validated_agent, capability)
            vault_result = load_vault_token()
            auth_info["vault_secret_loaded"] = vault_result.get("vault_secret_loaded", False)

            # Execute
            incident_text = arguments.get("incident_text", "")
            result = run_diagnostics(incident_text)
            result["authorization"] = auth_info
            result["safety"] = {
                "mutating_actions_taken": False,
                "notes": "Diagnostic analysis only - no changes made to systems"
            }

            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2)
                    }
                ]
            }

        elif tool_name == "execute_runbook":
            # Authorize
            capability = Capability.EXECUTE_RUNBOOK
            validated_agent = authorize(agent_id, capability)
            auth_info = get_authorization_info(validated_agent, capability)
            vault_result = load_vault_token()
            auth_info["vault_secret_loaded"] = vault_result.get("vault_secret_loaded", False)

            # Execute
            action = arguments.get("action", "")
            parameters = arguments.get("parameters", {})
            result = execute_runbook(action, parameters)

            response = {
                "runbook": result,
                "authorization": auth_info,
                "safety": {
                    "mutating_actions_taken": False,
                    "notes": "SIMULATED execution - no real changes made (hackathon mode)"
                }
            }

            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(response, indent=2)
                    }
                ]
            }

        elif tool_name == "get_secret":
            # Authorize
            capability = Capability.GET_SECRET
            validated_agent = authorize(agent_id, capability)
            auth_info = get_authorization_info(validated_agent, capability)
            vault_result = load_vault_token()
            auth_info["vault_secret_loaded"] = vault_result.get("vault_secret_loaded", False)

            # Execute
            name = arguments.get("name", "")
            result = get_secret(name)
            result["authorization"] = auth_info

            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2)
                    }
                ]
            }
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Unknown tool: {tool_name}"
                    }
                ],
                "isError": True
            }

    except ValueError as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Bad Request: {str(e)}"
                }
            ],
            "isError": True
        }
    except PermissionError as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Forbidden: {str(e)}"
                }
            ],
            "isError": True
        }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error: {str(e)}"
                }
            ],
            "isError": True
        }


def process_jsonrpc_message(message: dict) -> dict | None:
    """Process a JSON-RPC message and return response."""
    method = message.get("method")
    params = message.get("params", {})
    msg_id = message.get("id")

    # Notifications (no id) don't get responses
    if msg_id is None and method == "notifications/initialized":
        return None

    handlers = {
        "initialize": handle_initialize,
        "tools/list": handle_tools_list,
        "tools/call": handle_tools_call,
    }

    handler = handlers.get(method)
    if handler:
        try:
            result = handler(params)
            return create_jsonrpc_response(msg_id, result)
        except Exception as e:
            return create_jsonrpc_error(msg_id, -32603, f"Internal error: {str(e)}")
    else:
        # Method not found
        return create_jsonrpc_error(msg_id, -32601, f"Method not found: {method}")
