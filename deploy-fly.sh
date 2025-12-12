#!/bin/bash

# Fly.io Deployment Script

set -e

echo "✈️  Fly.io Deployment"
echo "===================="
echo ""

# Check if fly CLI is installed
if ! command -v fly &> /dev/null; then
    echo "📦 Installing Fly.io CLI..."
    curl -L https://fly.io/install.sh | sh
    echo ""
    echo "⚠️  Please restart your terminal or run:"
    echo "   export PATH=\"\$HOME/.fly/bin:\$PATH\""
    echo ""
    read -p "Press Enter after restarting terminal or adding to PATH..."
fi

# Check if logged in
if ! fly auth whoami &> /dev/null; then
    echo "🔐 Logging in to Fly.io..."
    fly auth login
fi

echo "✅ Authenticated"

# Check if app already exists
if fly apps list | grep -q "fraud-detection-api"; then
    echo "✅ App 'fraud-detection-api' already exists"
    read -p "Deploy to existing app? (y/n): " DEPLOY
    if [ "$DEPLOY" == "y" ]; then
        fly deploy
        exit 0
    fi
fi

# Launch new app
echo "🚀 Creating new Fly.io app..."
fly launch --name fraud-detection-api --region ord --no-deploy

echo ""
echo "📝 Review fly.toml and adjust if needed"
echo ""

read -p "Ready to deploy? (y/n): " READY
if [ "$READY" == "y" ]; then
    echo "🚀 Deploying..."
    fly deploy
    
    echo ""
    echo "✅ Deployment complete!"
    echo ""
    echo "🌐 Your app is at:"
    fly open
    echo ""
    echo "📊 View logs:"
    echo "   fly logs"
    echo ""
    echo "📈 View metrics:"
    echo "   fly dashboard"
else
    echo "Deployment cancelled. Run 'fly deploy' when ready."
fi

