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

EXPOSE 8000

# Use shell form to allow variable expansion
# Use shell form to ensure PORT variable is expanded
CMD ["sh", "-c", "./start.sh"]
