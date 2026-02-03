@echo off
REM A.E.G.I.S. Service Testing Script
REM IBM Dev Day Hackathon 2026

echo ========================================
echo A.E.G.I.S. Decision Service - Test Suite
echo ========================================
echo.

set SERVICE_URL=https://your-aegis-service-url.codeengine.appdomain.cloud

echo [1/4] Testing Health Endpoint...
curl -s %SERVICE_URL%/health
echo.
echo.

echo [2/4] Testing Version Endpoint...
curl -s %SERVICE_URL%/version
echo.
echo.

echo [3/4] Testing HIGH CONFIDENCE Scenario (Storage Incident)...
echo Input: Disk usage at 95%%, log rotation failed
curl -s -X POST %SERVICE_URL%/evaluate-incident ^
  -H "Content-Type: application/json" ^
  -d @test-high-confidence.json
echo.
echo.

echo [4/4] Testing LOW CONFIDENCE Scenario (Auth Incident)...
echo Input: Intermittent auth failures, no clear pattern
curl -s -X POST %SERVICE_URL%/evaluate-incident ^
  -H "Content-Type: application/json" ^
  -d @test-low-confidence.json
echo.
echo.

echo ========================================
echo Test Suite Complete!
echo ========================================
echo.
echo Expected Results:
echo - High Confidence: score ^>= 80, action = clear_logs
echo - Low Confidence: score ^< 80, action = escalate_to_human
echo.
