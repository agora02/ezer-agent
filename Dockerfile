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

# Copy all application files
COPY . .

# Ensure entrypoint is executable
RUN chmod +x entrypoint.sh

# Expose port
EXPOSE 8080

CMD ["./entrypoint.sh"]
