#!/bin/sh

# Default port if not provided (local dev)
PORT=${PORT:-8000}

echo "Starting app on port $PORT"

exec uvicorn app:app --host 0.0.0.0 --port "$PORT"
