# Production Dockerfile for Google Cloud Run Deployment
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    APP_HOME=/app

WORKDIR $APP_HOME

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Cloud Run injects $PORT (usually 8080)
EXPOSE 8080

# Run FastAPI app dynamically binding to Cloud Run $PORT
CMD uvicorn gateways.web_ui:app --host 0.0.0.0 --port ${PORT:-8080}
