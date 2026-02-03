"""MCP Tool implementations."""
import os
from typing import Any
from datetime import datetime, timezone


def get_secret(name: str) -> dict[str, str]:
    """
    Retrieve a secret value by name.

    Currently supports:
    - "execution_token": Returns AEGIS_EXEC_TOKEN env var
    """
    if name == "execution_token":
        value = os.environ.get("AEGIS_EXEC_TOKEN", "NOT_CONFIGURED")
        return {"name": name, "value": value}
    return {"name": name, "value": "NOT_FOUND"}


def run_diagnostics(incident_text: str) -> dict[str, Any]:
    """
    Run simulated diagnostics on an incident.

    Returns structured diagnostic output with likely causes,
    recommended steps, signals to check, and sample queries.
    """
    text_lower = incident_text.lower()

    likely_causes = []
    recommended_next_steps = []
    signals_to_check = []
    sample_queries = []

    # CPU-related patterns
    if "cpu" in text_lower or "processor" in text_lower:
        likely_causes.append("High CPU utilization from runaway process")
        likely_causes.append("Resource contention from concurrent workloads")
        recommended_next_steps.append("Identify top CPU-consuming processes")
        recommended_next_steps.append("Check for infinite loops or memory leaks")
        signals_to_check.append("CPU usage per process (top/htop)")
        signals_to_check.append("Load average trends")
        sample_queries.append("SELECT * FROM metrics WHERE metric='cpu_percent' AND value > 90")

    # Memory-related patterns
    if "memory" in text_lower or "ram" in text_lower or "oom" in text_lower:
        likely_causes.append("Memory leak in application")
        likely_causes.append("Insufficient allocated memory for workload")
        recommended_next_steps.append("Check memory consumption by process")
        recommended_next_steps.append("Review recent deployments for memory regressions")
        signals_to_check.append("Memory usage percentage")
        signals_to_check.append("Swap utilization")
        sample_queries.append("SELECT * FROM logs WHERE message LIKE '%OutOfMemory%'")

    # Disk-related patterns
    if "disk" in text_lower or "storage" in text_lower or "space" in text_lower:
        likely_causes.append("Disk space exhaustion from log accumulation")
        likely_causes.append("Large temporary files not cleaned up")
        recommended_next_steps.append("Identify largest files and directories")
        recommended_next_steps.append("Check log rotation configuration")
        signals_to_check.append("Disk usage by mount point")
        signals_to_check.append("Inode utilization")
        sample_queries.append("du -sh /* | sort -rh | head -10")

    # Network-related patterns
    if "network" in text_lower or "latency" in text_lower or "timeout" in text_lower:
        likely_causes.append("Network congestion or packet loss")
        likely_causes.append("DNS resolution delays")
        recommended_next_steps.append("Check network interface statistics")
        recommended_next_steps.append("Verify DNS resolver responsiveness")
        signals_to_check.append("Network latency to dependencies")
        signals_to_check.append("TCP retransmission rate")
        sample_queries.append("netstat -s | grep -i retransmit")

    # Default fallback if no patterns matched
    if not likely_causes:
        likely_causes.append("Unclassified incident - requires manual investigation")
        recommended_next_steps.append("Gather additional context from logs")
        recommended_next_steps.append("Check recent change history")
        signals_to_check.append("Application logs")
        signals_to_check.append("System metrics dashboard")
        sample_queries.append("tail -100 /var/log/application.log")

    return {
        "incident": incident_text,
        "diagnostics": {
            "likely_causes": likely_causes,
            "recommended_next_steps": recommended_next_steps,
            "signals_to_check": signals_to_check,
            "sample_queries": sample_queries,
        },
    }


def execute_runbook(action: str, parameters: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Execute a simulated runbook action.

    Supported actions:
    - clear_logs: Simulate clearing old log files
    - restart_service: Simulate restarting a service
    - run_diagnostics: Trigger diagnostic analysis

    This is SIMULATED for hackathon - no real infrastructure changes.
    """
    parameters = parameters or {}
    timestamp = datetime.now(timezone.utc).isoformat()

    simulated_results = {
        "clear_logs": {
            "action": "clear_logs",
            "status": "simulated_success",
            "details": {
                "target_path": parameters.get("path", "/var/log/app/*.log.old"),
                "files_removed": 12,
                "space_recovered_mb": 847,
                "retention_days": parameters.get("retention_days", 7),
            },
            "execution_log": [
                f"[{timestamp}] Runbook 'clear_logs' initiated",
                f"[{timestamp}] Scanning for files older than {parameters.get('retention_days', 7)} days",
                f"[{timestamp}] Found 12 files matching criteria",
                f"[{timestamp}] SIMULATED: Files would be removed (hackathon mode)",
                f"[{timestamp}] Runbook completed successfully",
            ],
        },
        "restart_service": {
            "action": "restart_service",
            "status": "simulated_success",
            "details": {
                "service_name": parameters.get("service", "application-server"),
                "previous_state": "running",
                "new_state": "running",
                "restart_duration_ms": 2340,
                "health_check_passed": True,
            },
            "execution_log": [
                f"[{timestamp}] Runbook 'restart_service' initiated",
                f"[{timestamp}] Target service: {parameters.get('service', 'application-server')}",
                f"[{timestamp}] SIMULATED: Service stop command issued",
                f"[{timestamp}] SIMULATED: Waiting for graceful shutdown",
                f"[{timestamp}] SIMULATED: Service start command issued",
                f"[{timestamp}] SIMULATED: Health check passed",
                f"[{timestamp}] Runbook completed successfully",
            ],
        },
        "run_diagnostics": {
            "action": "run_diagnostics",
            "status": "simulated_success",
            "details": {
                "diagnostic_type": parameters.get("type", "full"),
                "checks_performed": [
                    "cpu_utilization",
                    "memory_usage",
                    "disk_space",
                    "network_connectivity",
                    "service_health",
                ],
                "issues_found": 2,
                "recommendations_generated": 4,
            },
            "execution_log": [
                f"[{timestamp}] Runbook 'run_diagnostics' initiated",
                f"[{timestamp}] Running comprehensive system diagnostics",
                f"[{timestamp}] CPU check: OK",
                f"[{timestamp}] Memory check: WARNING - 78% utilized",
                f"[{timestamp}] Disk check: OK",
                f"[{timestamp}] Network check: OK",
                f"[{timestamp}] Service health: WARNING - response time elevated",
                f"[{timestamp}] Runbook completed with findings",
            ],
        },
    }

    if action in simulated_results:
        result = simulated_results[action]
    else:
        result = {
            "action": action,
            "status": "unknown_action",
            "details": {
                "error": f"Unknown action '{action}'",
                "supported_actions": list(simulated_results.keys()),
            },
            "execution_log": [
                f"[{timestamp}] Runbook '{action}' not recognized",
                f"[{timestamp}] Supported actions: {', '.join(simulated_results.keys())}",
            ],
        }

    return result
