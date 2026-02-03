#!/bin/bash

# A.E.G.I.S. Deployment Script for IBM Code Engine
# This script deploys the Decision Service to IBM Cloud Code Engine

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}A.E.G.I.S. Code Engine Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if required variables are set
if [ -z "$IBM_CLOUD_API_KEY" ] || [ -z "$WATSONX_PROJECT_ID" ]; then
    echo -e "${RED}Error: Required environment variables not set${NC}"
    echo "Please set IBM_CLOUD_API_KEY and WATSONX_PROJECT_ID"
    echo ""
    echo "Example:"
    echo "  export IBM_CLOUD_API_KEY='your-api-key'"
    echo "  export WATSONX_PROJECT_ID='your-project-id'"
    exit 1
fi

# Configuration
PROJECT_NAME="aegis-project"
APP_NAME="aegis-decision-service"
REGION="us-south"

echo -e "${YELLOW}Configuration:${NC}"
echo "  Project: $PROJECT_NAME"
echo "  App: $APP_NAME"
echo "  Region: $REGION"
echo ""

# Check if IBM Cloud CLI is installed
if ! command -v ibmcloud &> /dev/null; then
    echo -e "${RED}Error: IBM Cloud CLI not found${NC}"
    echo "Install from: https://cloud.ibm.com/docs/cli"
    exit 1
fi

# Check if Code Engine plugin is installed
if ! ibmcloud plugin list | grep -q "code-engine"; then
    echo -e "${YELLOW}Installing Code Engine plugin...${NC}"
    ibmcloud plugin install code-engine
fi

# Login to IBM Cloud
echo -e "${YELLOW}Logging in to IBM Cloud...${NC}"
ibmcloud login --apikey "$IBM_CLOUD_API_KEY" -r "$REGION"

# Create or select Code Engine project
echo -e "${YELLOW}Setting up Code Engine project...${NC}"
if ibmcloud ce project list | grep -q "$PROJECT_NAME"; then
    echo "Project $PROJECT_NAME exists, selecting it..."
    ibmcloud ce project select --name "$PROJECT_NAME"
else
    echo "Creating new project $PROJECT_NAME..."
    ibmcloud ce project create --name "$PROJECT_NAME"
fi

# Build and deploy application
echo -e "${YELLOW}Deploying application...${NC}"
ibmcloud ce application create \
    --name "$APP_NAME" \
    --build-source . \
    --port 5000 \
    --min-scale 1 \
    --max-scale 3 \
    --cpu 0.5 \
    --memory 1G \
    --env IBM_CLOUD_API_KEY="$IBM_CLOUD_API_KEY" \
    --env WATSONX_PROJECT_ID="$WATSONX_PROJECT_ID" \
    --env WATSONX_URL="https://us-south.ml.cloud.ibm.com"

# Check deployment status
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Deployment Successful!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""

    # Get application URL
    APP_URL=$(ibmcloud ce application get --name "$APP_NAME" --output json | grep -o '"url":"[^"]*' | grep -o 'https://[^"]*')

    echo -e "${GREEN}Your A.E.G.I.S. Decision Service is now live at:${NC}"
    echo -e "${GREEN}$APP_URL${NC}"
    echo ""
    echo "Test the health endpoint:"
    echo "  curl $APP_URL"
    echo ""
    echo "Test the evaluation endpoint:"
    echo "  curl -X POST $APP_URL/evaluate-incident \\"
    echo "    -H 'Content-Type: application/json' \\"
    echo "    -d '{\"incident_text\": \"Test incident\", \"category\": \"unknown\"}'"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Copy the URL above"
    echo "2. Update the 'servers' section in openapi-spec.yaml with this URL"
    echo "3. Import the OpenAPI spec into watsonx Orchestrate"
    echo ""
else
    echo -e "${RED}Deployment failed. Check the error messages above.${NC}"
    exit 1
fi
