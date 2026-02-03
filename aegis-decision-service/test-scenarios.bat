@echo off
REM A.E.G.I.S. Test Scenarios Script for Windows
REM This script tests all demo scenarios against your deployed Decision Service

setlocal enabledelayedexpansion

REM Configuration
if "%1"=="" (
    set SERVICE_URL=http://localhost:5000
) else (
    set SERVICE_URL=%1
)

echo ========================================
echo A.E.G.I.S. Test Scenarios
echo ========================================
echo Testing against: %SERVICE_URL%
echo.

echo ========================================
echo Test 1: Health Check
echo ========================================
curl -s "%SERVICE_URL%"
echo.
echo.

echo ========================================
echo Test 2: High Confidence - Storage Issue
echo ========================================
echo Expected: confidence_score ^>= 80, recommended_action = clear_logs
curl -s -X POST "%SERVICE_URL%/evaluate-incident" -H "Content-Type: application/json" -d "{\"incident_text\": \"Application logs consuming 95%% disk space. Log rotation service failed at 3 AM. No active user sessions currently affected. Standard log cleanup procedures apply.\", \"category\": \"storage\"}"
echo.
echo.

echo ========================================
echo Test 3: Low Confidence - Auth Issue
echo ========================================
echo Expected: confidence_score ^< 80, recommended_action = escalate_to_human
curl -s -X POST "%SERVICE_URL%/evaluate-incident" -H "Content-Type: application/json" -d "{\"incident_text\": \"Multiple users reporting intermittent authentication failures over the past hour. No clear pattern in the logs. May be related to the deployment we pushed 2 hours ago, but not confirmed. Some users can log in successfully while others cannot.\", \"category\": \"auth\"}"
echo.
echo.

echo ========================================
echo Test 4: Database Latency - Moderate Confidence
echo ========================================
echo Expected: confidence_score 60-79, recommended_action = run_diagnostics or escalate_to_human
curl -s -X POST "%SERVICE_URL%/evaluate-incident" -H "Content-Type: application/json" -d "{\"incident_text\": \"High database latency detected. Average query time increased from 50ms to 2000ms over the last 30 minutes. Users experiencing slow page loads.\", \"category\": \"latency\"}"
echo.
echo.

echo ========================================
echo Test 5: Ambiguous Issue
echo ========================================
echo Expected: confidence_score ^< 50, recommended_action = escalate_to_human
curl -s -X POST "%SERVICE_URL%/evaluate-incident" -H "Content-Type: application/json" -d "{\"incident_text\": \"System acting weird. Not sure what is wrong. Please help.\", \"category\": \"unknown\"}"
echo.
echo.

echo ========================================
echo Test 6: watsonx.ai Connection
echo ========================================
curl -s "%SERVICE_URL%/test-connection"
echo.
echo.

echo ========================================
echo All tests completed
echo ========================================
echo.
echo Next steps:
echo 1. Verify high-confidence scenarios return confidence ^>= 80
echo 2. Verify low-confidence scenarios return confidence ^< 80
echo 3. Test these scenarios in watsonx Orchestrate
echo 4. Practice your demo narration
echo.

endlocal
