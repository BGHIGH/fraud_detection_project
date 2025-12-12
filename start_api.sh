#!/bin/bash

# Script to start the Fraud Detection API

echo "Starting Fraud Detection API..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -q -r requirements.txt
fi

# Check if model exists
if [ ! -f "Models/fraud_detection_model.pkl" ]; then
    echo "Warning: Model file not found at Models/fraud_detection_model.pkl"
    echo "Please ensure the model file is in the Models directory"
fi

# Start the API
echo "Starting API server on http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "Press Ctrl+C to stop"
echo ""

uvicorn app:app --host 0.0.0.0 --port 8000 --reload

