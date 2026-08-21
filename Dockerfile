# Production Dockerfile for Google Cloud Run Deployment
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
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

# Copy all application files
COPY . .

# Expose port (Cloud Run defaults to 8080)
EXPOSE 8080

# Start server directly via Python (Bulletproof Cloud Run entrypoint)
CMD ["python", "server.py"]
