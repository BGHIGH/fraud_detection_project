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

EXPOSE 8000

# Run app - Railway sets PORT automatically
# Use Python to read PORT from environment variable
CMD python -c "import os; port = int(os.environ.get('PORT', 8000)); import uvicorn; uvicorn.run('app:app', host='0.0.0.0', port=port)"
