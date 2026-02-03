"""
A.E.G.I.S. Decision Service - Main FastAPI Application

Automated Escalation & Governance Intelligence System

This service provides AI-powered incident analysis using IBM watsonx.ai Granite models
with confidence-based routing for watsonx Orchestrate.
"""

import os
import logging
from uuid import uuid4
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .models import (
    IncidentRequest,
    IncidentResponse,
    DecisionPolicy,
    HealthResponse,
    VersionResponse
)
from .watsonx_client import WatsonxClient, WATSONX_MODEL_ID, WATSONX_URL
from .runbook_context import get_runbook_context, format_runbook_for_prompt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global client instance
watsonx_client: WatsonxClient = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    # Startup
    global watsonx_client
    logger.info("Initializing A.E.G.I.S. Decision Service")
    watsonx_client = WatsonxClient()
    logger.info("Service initialized successfully")
    yield
    # Shutdown
    logger.info("Shutting down A.E.G.I.S. Decision Service")


# Initialize FastAPI app
app = FastAPI(
    title="A.E.G.I.S. Decision Service API",
    description="""
    Automated Escalation & Governance Intelligence System - Decision Service

    This API provides AI-powered incident analysis using IBM watsonx.ai Granite models.
    It evaluates incidents and returns structured decisions with confidence scores for
    watsonx Orchestrate to route appropriately.

    **Key Features:**
    - Incident analysis using Granite AI models
    - Confidence-based decision making
    - Runbook context integration (local + optional Langflow)
    - Safe escalation to human reviewers
    - Strict JSON contracts for enterprise orchestration

    **Decision Logic:**
    - If confidence_score >= 80: Safe for auto-execution
    - If confidence_score < 80: Escalate to human reviewer

    **Critical for watsonx Orchestrate:** The confidence_score field enables
    conditional branching in your orchestration workflow.
    """,
    version="2.0.0",
    contact={
        "name": "A.E.G.I.S. Team",
        "email": "aegis@example.com"
    },
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For hackathon; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to ensure safe fallback"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    # Return safe escalation response
    return JSONResponse(
        status_code=500,
        content={
            "analysis": "System error during request processing",
            "recommended_action": "escalate_to_human",
            "confidence_score": 10,
            "explanation": "An unexpected error occurred. Human review required for safety.",
            "runbook_context": "",
            "trace_id": str(uuid4()),
            "model_id": WATSONX_MODEL_ID,
            "policy": {
                "auto_execute_threshold": 80,
                "escalate_threshold": 80
            }
        }
    )


@app.get(
    "/",
    response_model=dict,
    summary="Root endpoint",
    description="Returns basic service information"
)
async def root():
    """Root endpoint"""
    return {
        "service": "A.E.G.I.S. Decision Service",
        "version": "2.0.0",
        "description": "AI-powered incident analysis with confidence-based routing",
        "endpoints": {
            "health": "/health",
            "version": "/version",
            "evaluate": "POST /evaluate-incident",
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns service health status"
)
async def health_check():
    """Health check endpoint"""
    try:
        # Simple health check - just verify client is initialized
        if watsonx_client is None:
            return HealthResponse(
                status="error",
                message="WatsonX client not initialized"
            )

        return HealthResponse(status="ok")
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="error",
            message=str(e)
        )


@app.get(
    "/version",
    response_model=VersionResponse,
    summary="Version information",
    description="Returns service version and configuration"
)
async def version():
    """Version information endpoint"""
    return VersionResponse(
        model_id=WATSONX_MODEL_ID,
        watsonx_url=WATSONX_URL
    )


@app.post(
    "/evaluate-incident",
    response_model=IncidentResponse,
    summary="Evaluate Incident",
    description="""
    Analyzes an incident report and returns a structured decision recommendation.

    The service uses IBM watsonx.ai Granite models to:
    - Analyze the incident context
    - Determine appropriate action
    - Calculate confidence score
    - Provide explanation for the decision

    **Decision Logic:**
    - If confidence_score >= 80: Safe for auto-execution
    - If confidence_score < 80: Escalate to human reviewer

    **Critical for watsonx Orchestrate:** The confidence_score field enables
    conditional branching in your orchestration workflow.
    """,
    responses={
        200: {
            "description": "Incident successfully evaluated",
            "content": {
                "application/json": {
                    "examples": {
                        "auto_execute": {
                            "summary": "High Confidence - Auto Execute",
                            "value": {
                                "analysis": "Disk space critically low due to failed log rotation",
                                "recommended_action": "clear_logs",
                                "confidence_score": 95,
                                "explanation": "Clear cause with standard remediation. Safe to auto-execute.",
                                "runbook_context": "Storage runbook context...",
                                "trace_id": "123e4567-e89b-12d3-a456-426614174000",
                                "model_id": "ibm/granite-3-8b-instruct",
                                "policy": {
                                    "auto_execute_threshold": 80,
                                    "escalate_threshold": 80
                                }
                            }
                        },
                        "escalate": {
                            "summary": "Low Confidence - Escalate",
                            "value": {
                                "analysis": "Authentication failures with unclear root cause",
                                "recommended_action": "escalate_to_human",
                                "confidence_score": 45,
                                "explanation": "Intermittent failures require human investigation.",
                                "runbook_context": "Auth runbook context...",
                                "trace_id": "123e4567-e89b-12d3-a456-426614174001",
                                "model_id": "ibm/granite-3-8b-instruct",
                                "policy": {
                                    "auto_execute_threshold": 80,
                                    "escalate_threshold": 80
                                }
                            }
                        }
                    }
                }
            }
        },
        400: {"description": "Bad request - invalid input"},
        500: {"description": "Server error - returns safe escalation response"}
    }
)
async def evaluate_incident(request: IncidentRequest):
    """
    Main endpoint for incident evaluation.

    This endpoint coordinates:
    1. Runbook context retrieval (local or Langflow)
    2. AI decision via watsonx.ai Granite
    3. Policy enforcement (confidence threshold)
    4. Response construction with trace ID
    """
    trace_id = str(uuid4())

    # Structured logging
    logger.info(
        "Evaluating incident",
        extra={
            "trace_id": trace_id,
            "category": request.category,
            "reporter_role": request.reporter_role,
            "incident_length": len(request.incident_text)
        }
    )

    try:
        # Step 1: Get runbook context
        runbook_context_raw = get_runbook_context(
            category=request.category,
            incident_text=request.incident_text
        )
        runbook_context_formatted = format_runbook_for_prompt(runbook_context_raw)

        logger.info(
            "Retrieved runbook context",
            extra={
                "trace_id": trace_id,
                "runbook_length": len(runbook_context_raw)
            }
        )

        # Step 2: Get AI decision
        model_decision = watsonx_client.get_decision(
            incident_text=request.incident_text,
            category=request.category,
            reporter_role=request.reporter_role,
            runbook_context=runbook_context_formatted
        )

        logger.info(
            "Received model decision",
            extra={
                "trace_id": trace_id,
                "recommended_action": model_decision.recommended_action,
                "confidence_score": model_decision.confidence_score
            }
        )

        # Step 3: Build response with policy
        response = IncidentResponse(
            analysis=model_decision.analysis,
            recommended_action=model_decision.recommended_action,
            confidence_score=model_decision.confidence_score,
            explanation=model_decision.explanation,
            runbook_context=runbook_context_raw[:500],  # Truncate for response size
            trace_id=trace_id,
            model_id=WATSONX_MODEL_ID,
            policy=DecisionPolicy()
        )

        logger.info(
            "Incident evaluation complete",
            extra={
                "trace_id": trace_id,
                "final_action": response.recommended_action,
                "final_confidence": response.confidence_score
            }
        )

        return response

    except Exception as e:
        logger.error(
            f"Error evaluating incident: {e}",
            extra={"trace_id": trace_id},
            exc_info=True
        )

        # Return safe fallback
        return IncidentResponse(
            analysis="System error during analysis",
            recommended_action="escalate_to_human",
            confidence_score=10,
            explanation=f"An error occurred during analysis. Human review required. Error: {str(e)[:100]}",
            runbook_context="",
            trace_id=trace_id,
            model_id=WATSONX_MODEL_ID,
            policy=DecisionPolicy()
        )


# For local development
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(
        "src.aegis_service.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
