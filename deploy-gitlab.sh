#!/bin/bash

# GitLab Deployment Helper Script

set -e

echo "🚀 GitLab Deployment Helper"
echo "============================"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git not initialized. Initializing..."
    git init
fi

# Check if GitLab remote exists
if ! git remote | grep -q "origin"; then
    echo "📝 Please add your GitLab remote:"
    echo "   git remote add origin https://gitlab.com/your-username/fraud-detection-project.git"
    echo ""
    read -p "Enter your GitLab repository URL: " GITLAB_URL
    git remote add origin "$GITLAB_URL"
fi

# Check if model file exists
if [ ! -f "Models/fraud_detection_model.pkl" ]; then
    echo "⚠️  Warning: Model file not found at Models/fraud_detection_model.pkl"
    echo "   Make sure the model file exists before deploying!"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Add all files
echo "📦 Adding files to git..."
git add .

# Check if there are changes
if git diff --staged --quiet; then
    echo "✅ No changes to commit"
else
    read -p "Enter commit message (or press Enter for default): " COMMIT_MSG
    if [ -z "$COMMIT_MSG" ]; then
        COMMIT_MSG="Update: Fraud Detection System"
    fi
    git commit -m "$COMMIT_MSG"
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
if [ -z "$CURRENT_BRANCH" ]; then
    CURRENT_BRANCH="main"
    git checkout -b main
fi

echo ""
echo "📤 Pushing to GitLab..."
echo "   Branch: $CURRENT_BRANCH"
echo "   Remote: origin"
echo ""

# Push to GitLab
git push -u origin "$CURRENT_BRANCH"

echo ""
echo "✅ Code pushed to GitLab!"
echo ""
echo "📋 Next steps:"
echo "   1. Go to your GitLab project"
echo "   2. Navigate to CI/CD → Pipelines"
echo "   3. Click 'Run pipeline'"
echo "   4. Select your branch: $CURRENT_BRANCH"
echo "   5. Click 'Run pipeline'"
echo ""
echo "🔧 Configure CI/CD variables in:"
echo "   Settings → CI/CD → Variables"
echo ""
echo "📚 See GITLAB_DEPLOYMENT.md for detailed instructions"
echo ""

