FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p Models Data
RUN chmod +x start.sh

# Render ignores EXPOSE but it's ok
EXPOSE 8000

# Health check (optional but OK)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python - <<EOF
import requests, sys
try:
    requests.get("http://localhost:8000/health", timeout=5)
except Exception:
    sys.exit(1)
EOF

CMD ["./start.sh"]
