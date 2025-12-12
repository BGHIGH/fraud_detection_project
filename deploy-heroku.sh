#!/bin/bash

# Quick Heroku Deployment Script
# Usage: ./deploy-heroku.sh

set -e

echo "🚀 Fraud Detection API - Heroku Deployment"
echo "=========================================="

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not found. Please install it first:"
    echo "   curl https://cli-assets.heroku.com/install.sh | sh"
    exit 1
fi

# Check if logged in
echo "📋 Checking Heroku authentication..."
if ! heroku auth:whoami &> /dev/null; then
    echo "🔐 Please login to Heroku..."
    heroku login
fi

# Get app name
read -p "Enter Heroku app name (or press Enter for 'fraud-detection-api'): " APP_NAME
APP_NAME=${APP_NAME:-fraud-detection-api}

# Check if app exists
if heroku apps:info $APP_NAME &> /dev/null; then
    echo "✅ App '$APP_NAME' already exists"
else
    echo "📦 Creating new Heroku app: $APP_NAME"
    heroku create $APP_NAME
fi

# Initialize git if needed
if [ ! -d ".git" ]; then
    echo "📝 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit - Fraud Detection API"
fi

# Add Heroku remote
echo "🔗 Setting up Heroku remote..."
heroku git:remote -a $APP_NAME

# Check if model file exists
if [ ! -f "Models/fraud_detection_model.pkl" ]; then
    echo "⚠️  Warning: Model file not found!"
    echo "   Make sure Models/fraud_detection_model.pkl exists"
    read -p "Continue anyway? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ]; then
        exit 1
    fi
fi

# Deploy
echo "🚀 Deploying to Heroku..."
git add .
git commit -m "Deploy to Heroku" || echo "No changes to commit"
git push heroku main || git push heroku master

# Set environment variables
echo "⚙️  Setting environment variables..."
heroku config:set PYTHONUNBUFFERED=1

# Open app
echo "✅ Deployment complete!"
echo "🌐 Opening your app..."
heroku open

echo ""
echo "📊 Useful commands:"
echo "   heroku logs --tail          # View logs"
echo "   heroku ps                   # Check dyno status"
echo "   heroku config               # View config vars"
echo "   heroku restart              # Restart app"


