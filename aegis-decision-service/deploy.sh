#!/bin/bash

# A.E.G.I.S. Decision Service - Deployment Script for IBM Code Engine
# Region: EU-GB

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}A.E.G.I.S. Decision Service Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Configuration - SET THESE BEFORE RUNNING
# Get API_KEY from: IBM Cloud Console > Manage > Access (IAM) > API Keys
API_KEY="${WATSONX_APIKEY:-your_ibm_cloud_api_key_here}"
# Get PROJECT_ID from: watsonx.ai > Projects > (select your project) > Manage tab
PROJECT_ID="${WATSONX_PROJECT_ID:-your_watsonx_project_id_here}"
REGION="eu-gb"  # Change to your preferred region
CE_PROJECT_NAME="your-code-engine-project-name"
CE_PROJECT_ID="${CE_PROJECT_ID:-your_code_engine_project_id_here}"
APP_NAME="aegis-decision-service"

echo -e "${YELLOW}Configuration:${NC}"
echo "  Region: $REGION"
echo "  Code Engine Project: $CE_PROJECT_NAME"
echo "  Application: $APP_NAME"
echo ""

# Check if IBM Cloud CLI is installed
if ! command -v ibmcloud &> /dev/null; then
    echo -e "${RED}Error: IBM Cloud CLI not found${NC}"
    echo "Install from: https://cloud.ibm.com/docs/cli"
    echo ""
    echo "Quick install:"
    echo "  curl -fsSL https://clis.cloud.ibm.com/install/linux | sh"
    exit 1
fi

# Check if Code Engine plugin is installed
if ! ibmcloud plugin list | grep -q "code-engine"; then
    echo -e "${YELLOW}Installing Code Engine plugin...${NC}"
    ibmcloud plugin install code-engine -f
fi

# Login to IBM Cloud
echo -e "${YELLOW}Logging in to IBM Cloud...${NC}"
ibmcloud login --apikey "$API_KEY" -r "$REGION"

# Target the Code Engine project
echo -e "${YELLOW}Targeting Code Engine project...${NC}"
ibmcloud ce project select --id "$CE_PROJECT_ID"

# Check if application already exists
if ibmcloud ce app get --name "$APP_NAME" &> /dev/null; then
    echo -e "${YELLOW}Application exists. Updating...${NC}"

    # Update existing application
    ibmcloud ce app update \
        --name "$APP_NAME" \
        --build-source . \
        --build-context-dir . \
        --port 5000 \
        --min-scale 1 \
        --max-scale 3 \
        --cpu 0.5 \
        --memory 1G \
        --env WATSONX_APIKEY="$API_KEY" \
        --env WATSONX_PROJECT_ID="$PROJECT_ID" \
        --env WATSONX_URL="https://${REGION}.ml.cloud.ibm.com" \
        --env WATSONX_MODEL_ID="ibm/granite-3-8b-instruct" \
        --env PORT="5000" \
        --wait
else
    echo -e "${YELLOW}Creating new application...${NC}"

    # Create new application
    ibmcloud ce app create \
        --name "$APP_NAME" \
        --build-source . \
        --build-context-dir . \
        --port 5000 \
        --min-scale 1 \
        --max-scale 3 \
        --cpu 0.5 \
        --memory 1G \
        --env WATSONX_APIKEY="$API_KEY" \
        --env WATSONX_PROJECT_ID="$PROJECT_ID" \
        --env WATSONX_URL="https://${REGION}.ml.cloud.ibm.com" \
        --env WATSONX_MODEL_ID="ibm/granite-3-8b-instruct" \
        --env PORT="5000" \
        --wait
fi

# Get application URL
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Successful!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

APP_URL=$(ibmcloud ce app get --name "$APP_NAME" --output json | grep -o '"url":"[^"]*' | cut -d'"' -f4)

if [ -z "$APP_URL" ]; then
    echo -e "${YELLOW}Getting application URL...${NC}"
    APP_URL=$(ibmcloud ce app get --name "$APP_NAME" | grep "URL:" | awk '{print $2}')
fi

echo -e "${GREEN}Your A.E.G.I.S. Decision Service is now live at:${NC}"
echo -e "${GREEN}$APP_URL${NC}"
echo ""

echo "Test commands:"
echo ""
echo "Health check:"
echo "  curl $APP_URL/health"
echo ""
echo "Version info:"
echo "  curl $APP_URL/version"
echo ""
echo "Evaluate incident (high confidence):"
echo "  curl -X POST $APP_URL/evaluate-incident \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"incident_text\": \"Disk usage at 95%. Log rotation failed. No user impact.\", \"category\": \"storage\"}'"
echo ""
echo "Interactive API docs:"
echo "  Open in browser: $APP_URL/docs"
echo ""

# Save URL to file for later use
echo "$APP_URL" > deployment-url.txt
echo -e "${YELLOW}URL saved to: deployment-url.txt${NC}"
echo ""

echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Test the endpoints above"
echo "2. Run: python scripts/export_openapi.py (and update with this URL)"
echo "3. Import openapi.yaml into watsonx Orchestrate"
echo ""
