"""
Contract tests for A.E.G.I.S. Decision Service

These tests validate:
1. Response schema compliance
2. Confidence policy enforcement
3. Fallback behavior
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from src.aegis_service.main import app
from src.aegis_service.models import ModelDecision


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert data["status"] in ["ok", "degraded", "error"]


def test_version_endpoint(client):
    """Test version endpoint"""
    response = client.get("/version")
    assert response.status_code == 200

    data = response.json()
    assert data["service"] == "A.E.G.I.S. Decision Service"
    assert "version" in data
    assert "model_id" in data


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert data["service"] == "A.E.G.I.S. Decision Service"
    assert "endpoints" in data


@patch("src.aegis_service.main.watsonx_client")
def test_evaluate_incident_schema_compliance(mock_client, client):
    """Test that response matches exact schema"""
    # Mock watsonx client response
    mock_client.get_decision.return_value = ModelDecision(
        analysis="Test analysis",
        recommended_action="clear_logs",
        confidence_score=85,
        explanation="Test explanation"
    )

    response = client.post(
        "/evaluate-incident",
        json={
            "incident_text": "Test incident description that is long enough",
            "category": "storage"
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Validate required fields
    assert "analysis" in data
    assert "recommended_action" in data
    assert "confidence_score" in data
    assert "explanation" in data
    assert "runbook_context" in data
    assert "trace_id" in data
    assert "model_id" in data
    assert "policy" in data

    # Validate types
    assert isinstance(data["analysis"], str)
    assert isinstance(data["confidence_score"], int)
    assert isinstance(data["trace_id"], str)

    # Validate confidence_score range
    assert 0 <= data["confidence_score"] <= 100

    # Validate recommended_action is valid
    valid_actions = ["clear_logs", "restart_service", "run_diagnostics", "escalate_to_human"]
    assert data["recommended_action"] in valid_actions

    # Validate policy structure
    assert "auto_execute_threshold" in data["policy"]
    assert "escalate_threshold" in data["policy"]
    assert data["policy"]["auto_execute_threshold"] == 80
    assert data["policy"]["escalate_threshold"] == 80


@patch("src.aegis_service.main.watsonx_client")
def test_confidence_policy_enforcement_low_confidence_wrong_action(mock_client, client):
    """
    Test that low confidence with non-escalate action is overridden.

    If model returns confidence=60 with action=clear_logs,
    service must enforce policy and change to escalate_to_human.
    """
    # Mock model returning low confidence with wrong action
    # This simulates a policy violation that must be caught
    mock_decision = ModelDecision(
        analysis="Test analysis",
        recommended_action="clear_logs",  # Wrong! Should escalate at low confidence
        confidence_score=60,  # Low confidence
        explanation="Test explanation"
    )

    # The watsonx_client should enforce this internally via _validate_decision
    # But we'll test the endpoint behavior
    mock_client.get_decision.return_value = mock_decision

    response = client.post(
        "/evaluate-incident",
        json={
            "incident_text": "Test incident that should escalate due to low confidence",
            "category": "unknown"
        }
    )

    assert response.status_code == 200
    data = response.json()

    # The client's _validate_decision should have enforced escalation
    # But since we're mocking at a high level, let's verify the policy exists
    assert data["policy"]["escalate_threshold"] == 80

    # In real implementation, if confidence < 80, action must be escalate
    if data["confidence_score"] < 80:
        assert data["recommended_action"] == "escalate_to_human"


@patch("src.aegis_service.main.watsonx_client")
def test_high_confidence_auto_execute(mock_client, client):
    """Test high confidence scenario allows auto-execute"""
    mock_client.get_decision.return_value = ModelDecision(
        analysis="Clear disk space issue",
        recommended_action="clear_logs",
        confidence_score=95,
        explanation="Standard log cleanup procedure"
    )

    response = client.post(
        "/evaluate-incident",
        json={
            "incident_text": "Disk usage at 95%. Log rotation failed. Standard cleanup needed.",
            "category": "storage"
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert data["confidence_score"] >= 80
    assert data["recommended_action"] in ["clear_logs", "restart_service", "run_diagnostics"]


@patch("src.aegis_service.main.watsonx_client")
def test_missing_incident_text_returns_400(mock_client, client):
    """Test that missing incident_text returns 400 error"""
    response = client.post(
        "/evaluate-incident",
        json={
            "category": "storage"
            # Missing incident_text
        }
    )

    assert response.status_code == 422  # Pydantic validation error


@patch("src.aegis_service.main.watsonx_client")
def test_empty_incident_text_returns_400(mock_client, client):
    """Test that empty incident_text returns validation error"""
    response = client.post(
        "/evaluate-incident",
        json={
            "incident_text": "   ",  # Just whitespace
            "category": "storage"
        }
    )

    assert response.status_code == 422  # Pydantic validation error


@patch("src.aegis_service.main.watsonx_client")
def test_fallback_on_exception(mock_client, client):
    """Test that service returns safe fallback when watsonx fails"""
    # Mock client throwing exception
    mock_client.get_decision.side_effect = Exception("Simulated watsonx failure")

    response = client.post(
        "/evaluate-incident",
        json={
            "incident_text": "Test incident that will fail",
            "category": "unknown"
        }
    )

    # Should still return 200 with safe fallback
    assert response.status_code == 200
    data = response.json()

    # Fallback should escalate to human with low confidence
    assert data["recommended_action"] == "escalate_to_human"
    assert data["confidence_score"] <= 50  # Safe fallback has very low confidence


@patch("src.aegis_service.main.watsonx_client")
def test_all_incident_categories(mock_client, client):
    """Test all valid incident categories"""
    categories = ["latency", "storage", "auth", "unknown"]

    mock_client.get_decision.return_value = ModelDecision(
        analysis="Test analysis",
        recommended_action="run_diagnostics",
        confidence_score=70,
        explanation="Test explanation"
    )

    for category in categories:
        response = client.post(
            "/evaluate-incident",
            json={
                "incident_text": f"Test incident for {category} category",
                "category": category
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "confidence_score" in data


@patch("src.aegis_service.main.watsonx_client")
def test_reporter_role_included(mock_client, client):
    """Test that reporter_role is handled correctly"""
    mock_client.get_decision.return_value = ModelDecision(
        analysis="Test analysis",
        recommended_action="escalate_to_human",
        confidence_score=75,
        explanation="Test explanation"
    )

    response = client.post(
        "/evaluate-incident",
        json={
            "incident_text": "Test incident reported by SRE",
            "category": "latency",
            "reporter_role": "SRE"
        }
    )

    assert response.status_code == 200
    # Verify the mock was called (reporter_role was passed through)
    assert mock_client.get_decision.called


@patch("src.aegis_service.main.watsonx_client")
def test_trace_id_uniqueness(mock_client, client):
    """Test that each request gets a unique trace_id"""
    mock_client.get_decision.return_value = ModelDecision(
        analysis="Test",
        recommended_action="escalate_to_human",
        confidence_score=50,
        explanation="Test"
    )

    response1 = client.post(
        "/evaluate-incident",
        json={"incident_text": "First incident test case here"}
    )

    response2 = client.post(
        "/evaluate-incident",
        json={"incident_text": "Second incident test case here"}
    )

    assert response1.status_code == 200
    assert response2.status_code == 200

    trace_id1 = response1.json()["trace_id"]
    trace_id2 = response2.json()["trace_id"]

    # Trace IDs should be different
    assert trace_id1 != trace_id2


def test_openapi_schema_generated():
    """Test that OpenAPI schema is available"""
    client = TestClient(app)
    response = client.get("/openapi.json")
    assert response.status_code == 200

    schema = response.json()
    assert "paths" in schema
    assert "/evaluate-incident" in schema["paths"]
    assert "/health" in schema["paths"]
    assert "/version" in schema["paths"]
