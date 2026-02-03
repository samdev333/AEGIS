"""Agent badge policy enforcement for MCP tools."""
import os
from enum import Enum


class Capability(str, Enum):
    """Capabilities that can be authorized."""
    EXECUTE_RUNBOOK = "execute_runbook"
    RUN_DIAGNOSTICS = "run_diagnostics"
    GET_SECRET = "get_secret"


def get_execution_agent_id() -> str | None:
    """Get the Execution Agent ID from environment."""
    return os.environ.get("AEGIS_EXECUTION_AGENT_ID")


def get_triage_agent_id() -> str | None:
    """Get the Triage Agent ID from environment (optional)."""
    return os.environ.get("AEGIS_TRIAGE_AGENT_ID")


def get_allowed_agents(capability: Capability) -> set[str]:
    """
    Get the set of agent IDs allowed for a given capability.

    Policy rules:
    - execute_runbook: ONLY Execution Agent
    - get_secret: ONLY Execution Agent
    - run_diagnostics: Execution Agent + Triage Agent (if configured)
    """
    execution_id = get_execution_agent_id()
    triage_id = get_triage_agent_id()

    allowed: set[str] = set()

    if capability == Capability.EXECUTE_RUNBOOK:
        # Only Execution Agent can execute runbooks
        if execution_id:
            allowed.add(execution_id)

    elif capability == Capability.GET_SECRET:
        # Only Execution Agent can access secrets
        if execution_id:
            allowed.add(execution_id)

    elif capability == Capability.RUN_DIAGNOSTICS:
        # Both Execution and Triage agents can run diagnostics
        if execution_id:
            allowed.add(execution_id)
        if triage_id:
            allowed.add(triage_id)

    return allowed


def authorize(agent_id: str | None, capability: Capability) -> str:
    """
    Authorize an agent for a specific capability.

    Args:
        agent_id: The agent ID from the request
        capability: The capability being requested

    Returns:
        The validated agent_id if authorized

    Raises:
        ValueError: If agent_id is missing or empty (400)
        PermissionError: If agent is not allowed for this capability (403)
    """
    # Validate agent_id exists
    if not agent_id or not agent_id.strip():
        raise ValueError("agent_id is required and cannot be empty")

    agent_id = agent_id.strip()

    # Check if any agents are configured
    allowed_agents = get_allowed_agents(capability)
    if not allowed_agents:
        raise PermissionError(
            f"No agents configured for capability '{capability.value}'. "
            "Set AEGIS_EXECUTION_AGENT_ID environment variable."
        )

    # Check if this agent is allowed
    if agent_id not in allowed_agents:
        raise PermissionError(
            f"Agent '{agent_id}' is not authorized for capability '{capability.value}'"
        )

    return agent_id


def get_authorization_info(agent_id: str, capability: Capability) -> dict:
    """
    Get authorization info for audit-friendly response fields.

    Returns dict with:
    - authorized_agent_id
    - authorization_check
    - policy
    """
    return {
        "authorized_agent_id": agent_id,
        "authorization_check": "passed",
        "policy": capability.value,
    }
