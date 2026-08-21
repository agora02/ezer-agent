#!/bin/bash
# AE Agent One-Click Setup Script for Mac/Linux/Windows(WSL)

set -e

echo "🚀 [AE Agent] Starting Automated Environment Setup..."

# 1. Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.10+ is required. Please install Python."
    exit 1
fi

# 2. Create Virtual Environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment (venv)..."
    python3 -m venv venv
fi

# 3. Activate venv & install dependencies
echo "📥 Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. Prepare default config if .env does not exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating default .env from .env.example..."
    cp .env.example .env
fi

echo "========================================================"
echo "🎉 [AE Agent Setup Complete!]"
echo "========================================================"
echo "To start the Ezer Studio Web Dashboard:"
echo "  source venv/bin/activate && python -m uvicorn gateways.web_ui:app --host 0.0.0.0 --port 8888"
echo ""
echo "To start the Discord Bot:"
echo "  source venv/bin/activate && python scripts/auto_reloader.py"
echo "========================================================"
