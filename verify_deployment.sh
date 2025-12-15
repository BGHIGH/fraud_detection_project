#!/bin/bash

# Deployment Verification Script
# Usage: ./verify_deployment.sh <DEPLOYMENT_URL>
# Example: ./verify_deployment.sh https://fraud-detection-api.railway.app

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if URL is provided
if [ -z "$1" ]; then
    echo -e "${RED}❌ Error: Deployment URL required${NC}"
    echo "Usage: ./verify_deployment.sh <DEPLOYMENT_URL>"
    echo "Example: ./verify_deployment.sh https://fraud-detection-api.railway.app"
    exit 1
fi

DEPLOYMENT_URL="$1"
# Remove trailing slash if present
DEPLOYMENT_URL="${DEPLOYMENT_URL%/}"

echo -e "${BLUE}🔍 Verifying Deployment: ${DEPLOYMENT_URL}${NC}"
echo "=========================================="
echo ""

# Test 1: Check if app is accessible
echo -e "${YELLOW}1. Testing if app is accessible...${NC}"
if curl -s -f -o /dev/null -w "%{http_code}" "${DEPLOYMENT_URL}/health" | grep -q "200"; then
    echo -e "${GREEN}✅ App is accessible!${NC}"
else
    echo -e "${RED}❌ App is not accessible${NC}"
    echo "   Trying to connect to: ${DEPLOYMENT_URL}/health"
    exit 1
fi
echo ""

# Test 2: Health check endpoint
echo -e "${YELLOW}2. Testing /health endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s "${DEPLOYMENT_URL}/health")
if echo "$HEALTH_RESPONSE" | grep -q "status"; then
    echo -e "${GREEN}✅ Health check passed!${NC}"
    echo "   Response: $HEALTH_RESPONSE"
else
    echo -e "${RED}❌ Health check failed${NC}"
    echo "   Response: $HEALTH_RESPONSE"
fi
echo ""

# Test 3: API info endpoint
echo -e "${YELLOW}3. Testing /api endpoint...${NC}"
API_RESPONSE=$(curl -s "${DEPLOYMENT_URL}/api")
if echo "$API_RESPONSE" | grep -q "Fraud Detection"; then
    echo -e "${GREEN}✅ API info endpoint working!${NC}"
    echo "   Response: $API_RESPONSE"
else
    echo -e "${RED}❌ API info endpoint failed${NC}"
    echo "   Response: $API_RESPONSE"
fi
echo ""

# Test 4: Web interface
echo -e "${YELLOW}4. Testing web interface (/)...${NC}"
WEB_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${DEPLOYMENT_URL}/")
if [ "$WEB_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ Web interface is accessible!${NC}"
    echo "   Status: $WEB_STATUS"
else
    echo -e "${YELLOW}⚠️  Web interface returned status: $WEB_STATUS${NC}"
fi
echo ""

# Test 5: Predict endpoint (single prediction)
echo -e "${YELLOW}5. Testing /predict endpoint...${NC}"
PREDICT_PAYLOAD='{
  "transaction_amount": 100.50,
  "avg_transaction_amount_7d": 50.25,
  "failed_transaction_count_7d": 0,
  "daily_transaction_count": 5,
  "risk_score": 0.3,
  "card_age": 365,
  "account_balance": 1000.0,
  "transaction_type": "Online",
  "device_type": "Mobile",
  "location": "US",
  "merchant_category": "Retail",
  "authentication_method": "PIN"
}'

PREDICT_RESPONSE=$(curl -s -X POST "${DEPLOYMENT_URL}/predict" \
  -H "Content-Type: application/json" \
  -d "$PREDICT_PAYLOAD")

if echo "$PREDICT_RESPONSE" | grep -q "prediction\|is_fraud"; then
    echo -e "${GREEN}✅ Predict endpoint working!${NC}"
    echo "   Response: $PREDICT_RESPONSE"
else
    echo -e "${RED}❌ Predict endpoint failed${NC}"
    echo "   Response: $PREDICT_RESPONSE"
fi
echo ""

# Test 6: Metrics endpoint
echo -e "${YELLOW}6. Testing /metrics endpoint...${NC}"
METRICS_RESPONSE=$(curl -s "${DEPLOYMENT_URL}/metrics")
if echo "$METRICS_RESPONSE" | grep -q "total_requests\|predictions"; then
    echo -e "${GREEN}✅ Metrics endpoint working!${NC}"
    echo "   Response: $METRICS_RESPONSE"
else
    echo -e "${YELLOW}⚠️  Metrics endpoint may not be working as expected${NC}"
    echo "   Response: $METRICS_RESPONSE"
fi
echo ""

# Summary
echo "=========================================="
echo -e "${BLUE}📊 Verification Summary${NC}"
echo "=========================================="
echo -e "${GREEN}✅ All critical endpoints tested!${NC}"
echo ""
echo -e "${BLUE}📝 Next steps:${NC}"
echo "   1. Open ${DEPLOYMENT_URL} in your browser"
echo "   2. Test the web interface"
echo "   3. Check API documentation at ${DEPLOYMENT_URL}/docs"
echo "   4. Monitor logs for any errors"
echo ""

