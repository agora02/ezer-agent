#!/bin/bash
PORT="${PORT:-8080}"
echo "🚀 Starting Ezer Agent server on port $PORT..."
exec uvicorn gateways.web_ui:app --host 0.0.0.0 --port "$PORT"
