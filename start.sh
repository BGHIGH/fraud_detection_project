#!/bin/sh
# Startup script for Railway - handles PORT variable correctly

# Get PORT from environment, default to 8000
if [ -z "$PORT" ]; then
    PORT=8000
fi

echo "Starting app on port $PORT"

# Use Python to ensure PORT is properly read
exec python -c "import os; import uvicorn; port = int(os.environ.get('PORT', 8000)); uvicorn.run('app:app', host='0.0.0.0', port=port)"
