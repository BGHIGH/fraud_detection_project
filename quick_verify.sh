#!/bin/bash

# Quick Deployment Verification
# Replace YOUR_RAILWAY_URL with your actual Railway URL

RAILWAY_URL="${1:-YOUR_RAILWAY_URL}"

if [ "$RAILWAY_URL" = "YOUR_RAILWAY_URL" ]; then
    echo "❌ Please provide your Railway URL"
    echo "Usage: ./quick_verify.sh https://your-app.railway.app"
    exit 1
fi

echo "🔍 Testing Railway Deployment: $RAILWAY_URL"
echo ""

# Test 1: Health Check
echo "1. Health Check..."
HEALTH=$(curl -s "$RAILWAY_URL/health")
if echo "$HEALTH" | grep -q "healthy"; then
    echo "   ✅ App is healthy!"
    echo "   Response: $HEALTH"
else
    echo "   ❌ Health check failed"
    echo "   Response: $HEALTH"
fi
echo ""

# Test 2: API Info
echo "2. API Info..."
API=$(curl -s "$RAILWAY_URL/api")
if echo "$API" | grep -q "Fraud Detection"; then
    echo "   ✅ API is working!"
else
    echo "   ❌ API check failed"
fi
echo ""

# Test 3: Web Interface
echo "3. Web Interface..."
WEB_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$RAILWAY_URL/")
if [ "$WEB_STATUS" = "200" ]; then
    echo "   ✅ Web interface accessible!"
else
    echo "   ⚠️  Web interface status: $WEB_STATUS"
fi
echo ""

# Test 4: Prediction
echo "4. Testing Prediction..."
PREDICT_RESPONSE=$(curl -s -X POST "$RAILWAY_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{
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
  }')

if echo "$PREDICT_RESPONSE" | grep -q "prediction\|is_fraud"; then
    echo "   ✅ Prediction working!"
    echo "   Response: $PREDICT_RESPONSE"
else
    echo "   ❌ Prediction failed"
    echo "   Response: $PREDICT_RESPONSE"
fi
echo ""

echo "✅ Verification complete!"
echo ""
echo "🌐 Open in browser: $RAILWAY_URL"
echo "📚 API Docs: $RAILWAY_URL/docs"

