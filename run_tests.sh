#!/bin/bash

# Script to run all tests for Fraud Detection API

echo "=========================================="
echo "Running Fraud Detection API Tests"
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Run unit tests
echo ""
echo "Running unit tests..."
echo "=========================================="
pytest tests/ -v --tb=short

# Check if tests passed
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "All tests passed!"
    echo "=========================================="
else
    echo ""
    echo "=========================================="
    echo "Some tests failed!"
    echo "=========================================="
    exit 1
fi

