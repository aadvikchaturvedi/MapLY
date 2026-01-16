#!/bin/bash

# ============================================
# MapLY ML Services - Startup Script
# ============================================

set -e

echo "🚀 Starting MapLY ML Services..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "✓ Created .env file. Please review and update settings if needed."
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
fi

# Start the server
echo "🌐 Starting API server..."
python -m uvicorn api.main:app \
    --host ${API_HOST:-0.0.0.0} \
    --port ${API_PORT:-8000} \
    --reload

echo "✓ MapLY ML Services started successfully!"
