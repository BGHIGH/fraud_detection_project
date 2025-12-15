#!/bin/bash

# Railway Deployment Helper Script
# This script helps you prepare for Railway deployment

set -e

echo "🚂 Railway Deployment Preparation"
echo "=================================="
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📝 Initializing git repository..."
    git init
    echo "✅ Git initialized"
else
    echo "✅ Git repository already exists"
fi

# Check if model file exists
if [ ! -f "Models/fraud_detection_model.pkl" ]; then
    echo "⚠️  WARNING: Model file not found!"
    echo "   Make sure Models/fraud_detection_model.pkl exists"
    read -p "Continue anyway? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ]; then
        exit 1
    fi
else
    echo "✅ Model file found"
fi

# Check Dockerfile
if [ ! -f "Dockerfile" ]; then
    echo "❌ Dockerfile not found!"
    exit 1
else
    echo "✅ Dockerfile found"
fi

# Check requirements.txt
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found!"
    exit 1
else
    echo "✅ requirements.txt found"
fi

echo ""
echo "📋 Next Steps:"
echo "=============="
echo ""
echo "1. Create a GitHub repository:"
echo "   - Go to https://github.com/new"
echo "   - Create a new repository"
echo "   - Name it: fraud-detection-api"
echo ""
echo "2. Push your code to GitHub:"
echo "   git add ."
echo "   git commit -m 'Ready for Railway deployment'"
echo "   git remote add origin https://github.com/YOUR_USERNAME/fraud-detection-api.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Deploy on Railway:"
echo "   - Go to https://railway.app"
echo "   - Sign up (free, no credit card needed)"
echo "   - Click 'New Project'"
echo "   - Select 'Deploy from GitHub repo'"
echo "   - Choose your repository"
echo "   - Railway will auto-detect Docker and deploy!"
echo ""
echo "4. Get your URL:"
echo "   - Railway will give you a URL like:"
echo "     https://fraud-detection-api.up.railway.app"
echo ""
echo "✅ Your app will be live in minutes!"
echo ""

# Ask if user wants to test Docker locally
read -p "Test Docker build locally first? (y/n): " TEST_DOCKER
if [ "$TEST_DOCKER" == "y" ]; then
    echo ""
    echo "🐳 Testing Docker build..."
    docker build -t fraud-detection-api .
    echo ""
    echo "✅ Docker build successful!"
    echo ""
    echo "To test locally, run:"
    echo "  docker run -p 8000:8000 fraud-detection-api"
    echo ""
    echo "Then visit: http://localhost:8000"
fi

