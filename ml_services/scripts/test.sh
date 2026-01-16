#!/bin/bash

# ============================================
# MapLY ML Services - Test Runner
# ============================================

set -e

echo "🧪 Running MapLY ML Services Tests..."

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run tests with coverage
echo "📊 Running tests with coverage..."
pytest tests/ \
    --verbose \
    --cov=. \
    --cov-report=html \
    --cov-report=term \
    --cov-report=xml \
    -v

echo "✓ Tests completed!"
echo "📄 Coverage report generated in htmlcov/index.html"
