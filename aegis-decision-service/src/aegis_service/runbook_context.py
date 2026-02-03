"""
Runbook Context Retrieval for A.E.G.I.S.

Supports both local markdown runbooks and optional remote Langflow integration.

Architecture:
1. Try local runbook files first (runbooks/{category}.md)
2. If LANGFLOW_RUNBOOK_URL is set, attempt remote fetch
3. Fallback to generic runbook if specific category not found
4. Always return valid context string (never None)
"""

import os
import logging
from pathlib import Path
from typing import Optional
import requests

logger = logging.getLogger(__name__)

# Configuration
RUNBOOK_DIR = Path(__file__).parent.parent.parent / "runbooks"
LANGFLOW_URL = os.environ.get("LANGFLOW_RUNBOOK_URL")
LANGFLOW_TIMEOUT = 3  # seconds


def get_local_runbook(category: str) -> str:
    """
    Load runbook from local markdown file.

    Args:
        category: Incident category (latency, storage, auth, unknown)

    Returns:
        Runbook content as string
    """
    runbook_file = RUNBOOK_DIR / f"{category}.md"

    try:
        if runbook_file.exists():
            content = runbook_file.read_text(encoding="utf-8")
            logger.info(f"Loaded local runbook for category: {category}")
            return content.strip()
        else:
            logger.warning(f"Runbook file not found: {runbook_file}, using fallback")
            # Fallback to unknown.md
            fallback_file = RUNBOOK_DIR / "unknown.md"
            if fallback_file.exists():
                return fallback_file.read_text(encoding="utf-8").strip()
            else:
                return _get_hardcoded_fallback(category)
    except Exception as e:
        logger.error(f"Error reading local runbook: {e}")
        return _get_hardcoded_fallback(category)


def get_langflow_runbook(category: str, incident_text: str) -> Optional[str]:
    """
    Fetch runbook context from remote Langflow endpoint.

    Args:
        category: Incident category
        incident_text: Full incident description

    Returns:
        Runbook context string or None if fetch fails
    """
    if not LANGFLOW_URL:
        return None

    try:
        logger.info(f"Fetching runbook from Langflow: {LANGFLOW_URL}")

        response = requests.post(
            LANGFLOW_URL,
            json={
                "category": category,
                "incident_text": incident_text
            },
            timeout=LANGFLOW_TIMEOUT,
            headers={"Content-Type": "application/json"}
        )

        response.raise_for_status()
        data = response.json()

        # Langflow should return {"context": "..."}
        context = data.get("context", "")

        if context:
            logger.info("Successfully retrieved runbook from Langflow")
            return context
        else:
            logger.warning("Langflow returned empty context")
            return None

    except requests.exceptions.Timeout:
        logger.warning(f"Langflow request timed out after {LANGFLOW_TIMEOUT}s")
        return None
    except requests.exceptions.RequestException as e:
        logger.warning(f"Langflow request failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching from Langflow: {e}")
        return None


def get_runbook_context(category: str, incident_text: str) -> str:
    """
    Get runbook context for an incident.

    Strategy:
    1. Try Langflow if configured
    2. Fall back to local runbooks
    3. Always return valid string (never None)

    Args:
        category: Incident category
        incident_text: Full incident description

    Returns:
        Runbook context string
    """
    # Try Langflow first if configured
    if LANGFLOW_URL:
        langflow_context = get_langflow_runbook(category, incident_text)
        if langflow_context:
            logger.info("Using Langflow runbook context")
            return langflow_context
        else:
            logger.info("Langflow unavailable, falling back to local runbooks")

    # Fall back to local runbooks
    local_context = get_local_runbook(category)
    logger.info("Using local runbook context")
    return local_context


def _get_hardcoded_fallback(category: str) -> str:
    """
    Hardcoded fallback runbooks if files are missing.

    This ensures the service always has runbook context available.
    """
    fallbacks = {
        "latency": """
## Latency Incident Runbook

**Investigation Steps:**
- Check network latency to dependencies
- Review recent query execution times
- Check for lock contention in database
- Verify index usage on slow queries
- Check connection pool saturation

**Common Remediation:**
- Run diagnostics to identify slow queries
- Optimize indexes if needed
- Scale resources if overloaded
""",
        "storage": """
## Storage Incident Runbook

**Investigation Steps:**
- Check disk space usage on all volumes
- Review log rotation configuration
- Identify large files or orphaned data
- Check for runaway log growth
- Verify backup processes not consuming space

**Common Remediation:**
- Clear old logs if log rotation failed
- Remove temporary files
- Archive or compress old data
- Increase disk space if needed
""",
        "auth": """
## Authentication Incident Runbook

**Investigation Steps:**
- Verify authentication service health
- Check token expiration policies
- Review recent failed login attempts
- Check for service outages
- Verify certificate validity
- Check API key rotation

**Common Remediation:**
- Restart authentication service if unhealthy
- Check for expired credentials
- Review recent deployment changes
- Escalate if unclear cause
""",
        "unknown": """
## General Incident Runbook

**Investigation Steps:**
- Gather complete system metrics
- Check application logs for errors
- Verify all critical services are running
- Review recent deployments or changes
- Check for known issues or alerts

**Common Remediation:**
- Run comprehensive diagnostics
- Escalate to human if unclear
- Document findings for future reference
"""
    }

    return fallbacks.get(category, fallbacks["unknown"]).strip()


def format_runbook_for_prompt(runbook_content: str) -> str:
    """
    Format runbook content for inclusion in AI prompt.

    Args:
        runbook_content: Raw runbook content

    Returns:
        Formatted runbook string for prompt injection
    """
    if not runbook_content:
        return ""

    return f"""
## Relevant Runbook Context

{runbook_content}

Use the above runbook context to inform your analysis and decision.
If the incident matches runbook patterns, increase confidence.
If the incident deviates from runbook patterns, decrease confidence.
"""
