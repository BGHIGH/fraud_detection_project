#!/bin/sh
# Startup script for Railway deployment
# Handles PORT environment variable correctly

# Get PORT from environment or default to 8000
PORT=${PORT:-8000}

# Run uvicorn with the port
exec uvicorn app:app --host 0.0.0.0 --port "$PORT"

