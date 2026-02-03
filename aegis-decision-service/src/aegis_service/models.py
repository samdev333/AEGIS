"""
Pydantic models for A.E.G.I.S. Decision Service

These models define the strict JSON contract between watsonx Orchestrate
and the Decision Service.
"""

from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator


class IncidentRequest(BaseModel):
    """Request model for incident evaluation"""

    incident_text: str = Field(
        ...,
        min_length=10,
        description="Detailed description of the incident",
        examples=["High database latency detected. Query times increased from 50ms to 2000ms."]
    )

    category: Optional[Literal["latency", "storage", "auth", "unknown"]] = Field(
        default="unknown",
        description="Incident category for context retrieval"
    )

    reporter_role: Optional[Literal["SRE", "Developer", "Manager", "Other"]] = Field(
        default="Other",
        description="Role of the person reporting the incident"
    )

    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context fields"
    )

    @field_validator("incident_text")
    @classmethod
    def validate_incident_text(cls, v: str) -> str:
        """Ensure incident text is not just whitespace"""
        if not v.strip():
            raise ValueError("incident_text cannot be empty or whitespace")
        return v.strip()


class DecisionPolicy(BaseModel):
    """Decision policy thresholds"""

    auto_execute_threshold: int = Field(
        default=80,
        description="Minimum confidence score for auto-execution"
    )

    escalate_threshold: int = Field(
        default=80,
        description="Below this threshold, must escalate to human"
    )


class IncidentResponse(BaseModel):
    """Response model for incident evaluation

    This is the strict JSON contract that watsonx Orchestrate relies on
    for conditional branching.
    """

    analysis: str = Field(
        ...,
        description="One-sentence summary of the incident",
        examples=["Database experiencing high latency due to unoptimized queries"]
    )

    recommended_action: Literal[
        "clear_logs",
        "restart_service",
        "run_diagnostics",
        "escalate_to_human"
    ] = Field(
        ...,
        description="Recommended action to take"
    )

    confidence_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Confidence level (0-100). Use this for branching in watsonx Orchestrate"
    )

    explanation: str = Field(
        ...,
        description="Brief explanation for human reviewer",
        examples=["Database latency suggests query optimization needed. Running diagnostics first."]
    )

    runbook_context: str = Field(
        default="",
        description="Runbook context used for analysis (may be empty)"
    )

    trace_id: str = Field(
        ...,
        description="Unique trace ID for this request"
    )

    model_id: str = Field(
        ...,
        description="watsonx.ai model used for analysis"
    )

    policy: DecisionPolicy = Field(
        default_factory=DecisionPolicy,
        description="Decision policy thresholds"
    )

    @field_validator("confidence_score")
    @classmethod
    def validate_confidence_and_action(cls, v: int) -> int:
        """Ensure confidence score is valid integer"""
        if not isinstance(v, int):
            raise ValueError("confidence_score must be an integer")
        return v


class ModelDecision(BaseModel):
    """Internal model for AI-generated decision (before policy enforcement)"""

    analysis: str
    recommended_action: Literal[
        "clear_logs",
        "restart_service",
        "run_diagnostics",
        "escalate_to_human"
    ]
    confidence_score: int = Field(ge=0, le=100)
    explanation: str


class HealthResponse(BaseModel):
    """Health check response"""

    status: Literal["ok", "degraded", "error"] = "ok"
    message: Optional[str] = None


class VersionResponse(BaseModel):
    """Version information response"""

    service: str = "A.E.G.I.S. Decision Service"
    version: str = "2.0.0"
    model_id: str
    watsonx_url: str
