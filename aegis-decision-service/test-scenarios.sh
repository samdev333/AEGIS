#!/bin/bash

# A.E.G.I.S. Test Scenarios Script
# This script tests all demo scenarios against your deployed Decision Service

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
SERVICE_URL="${1:-http://localhost:5000}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}A.E.G.I.S. Test Scenarios${NC}"
echo -e "${GREEN}========================================${NC}"
echo "Testing against: $SERVICE_URL"
echo ""

# Test 1: Health Check
echo -e "${YELLOW}Test 1: Health Check${NC}"
curl -s "$SERVICE_URL" | jq '.'
echo ""

# Test 2: High Confidence - Storage Issue (Auto-Execute)
echo -e "${YELLOW}Test 2: High Confidence - Storage Issue${NC}"
echo "Expected: confidence_score >= 80, recommended_action = clear_logs"
curl -s -X POST "$SERVICE_URL/evaluate-incident" \
  -H "Content-Type: application/json" \
  -d '{
    "incident_text": "Application logs consuming 95% disk space. Log rotation service failed at 3 AM. No active user sessions currently affected. Standard log cleanup procedures apply.",
    "category": "storage"
  }' | jq '{confidence_score: .confidence_score, recommended_action: .recommended_action, analysis: .analysis}'
echo ""

# Test 3: Low Confidence - Auth Issue (Escalate)
echo -e "${YELLOW}Test 3: Low Confidence - Auth Issue${NC}"
echo "Expected: confidence_score < 80, recommended_action = escalate_to_human"
curl -s -X POST "$SERVICE_URL/evaluate-incident" \
  -H "Content-Type: application/json" \
  -d '{
    "incident_text": "Multiple users reporting intermittent authentication failures over the past hour. No clear pattern in the logs. May be related to the deployment we pushed 2 hours ago, but not confirmed. Some users can log in successfully while others cannot.",
    "category": "auth"
  }' | jq '{confidence_score: .confidence_score, recommended_action: .recommended_action, analysis: .analysis}'
echo ""

# Test 4: Database Latency (Moderate)
echo -e "${YELLOW}Test 4: Database Latency - Moderate Confidence${NC}"
echo "Expected: confidence_score 60-79, recommended_action = run_diagnostics or escalate_to_human"
curl -s -X POST "$SERVICE_URL/evaluate-incident" \
  -H "Content-Type: application/json" \
  -d '{
    "incident_text": "High database latency detected. Average query time increased from 50ms to 2000ms over the last 30 minutes. Users experiencing slow page loads.",
    "category": "latency"
  }' | jq '{confidence_score: .confidence_score, recommended_action: .recommended_action, analysis: .analysis}'
echo ""

# Test 5: Ambiguous Issue (Low Confidence)
echo -e "${YELLOW}Test 5: Ambiguous Issue${NC}"
echo "Expected: confidence_score < 50, recommended_action = escalate_to_human"
curl -s -X POST "$SERVICE_URL/evaluate-incident" \
  -H "Content-Type: application/json" \
  -d '{
    "incident_text": "System acting weird. Not sure what is wrong. Please help.",
    "category": "unknown"
  }' | jq '{confidence_score: .confidence_score, recommended_action: .recommended_action, analysis: .analysis}'
echo ""

# Test 6: Connection Test
echo -e "${YELLOW}Test 6: watsonx.ai Connection${NC}"
curl -s "$SERVICE_URL/test-connection" | jq '.'
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}All tests completed${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Verify high-confidence scenarios return confidence >= 80"
echo "2. Verify low-confidence scenarios return confidence < 80"
echo "3. Test these scenarios in watsonx Orchestrate"
echo "4. Practice your demo narration"
