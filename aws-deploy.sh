#!/bin/bash

# AWS Deployment Script for Fraud Detection API
# This script helps deploy the API to AWS ECS or EC2

set -e

REGION=${AWS_REGION:-us-east-1}
ECR_REPO=${ECR_REPO:-fraud-detection-api}
ECS_CLUSTER=${ECS_CLUSTER:-fraud-detection-cluster}
ECS_SERVICE=${ECS_SERVICE:-fraud-detection-service}

echo "=========================================="
echo "AWS Deployment Script"
echo "=========================================="
echo "Region: $REGION"
echo "ECR Repository: $ECR_REPO"
echo ""

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPO}"

echo "AWS Account ID: $AWS_ACCOUNT_ID"
echo "ECR URI: $ECR_URI"
echo ""

# Build Docker image
echo "Building Docker image..."
docker build -t $ECR_REPO:latest .

# Login to ECR
echo "Logging in to ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_URI

# Create ECR repository if it doesn't exist
echo "Creating ECR repository if needed..."
aws ecr describe-repositories --repository-names $ECR_REPO --region $REGION 2>/dev/null || \
    aws ecr create-repository --repository-name $ECR_REPO --region $REGION

# Tag and push image
echo "Tagging and pushing image..."
docker tag $ECR_REPO:latest $ECR_URI:latest
docker push $ECR_URI:latest

echo ""
echo "=========================================="
echo "Image pushed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Update your ECS task definition to use: $ECR_URI:latest"
echo "2. Update your ECS service:"
echo "   aws ecs update-service --cluster $ECS_CLUSTER --service $ECS_SERVICE --force-new-deployment --region $REGION"
echo ""

