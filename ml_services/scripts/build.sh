#!/bin/bash

# ============================================
# MapLY ML Services - Docker Build Script
# ============================================

set -e

echo "Building MapLY ML Services Docker Image..."

# Get version from config or use default
VERSION=${1:-latest}

echo "📦 Building version: $VERSION"

# Build the Docker image
docker build \
    -t maply-ml-services:$VERSION \
    -t maply-ml-services:latest \
    .

echo "✓ Docker image built successfully!"
echo "🏷️  Tagged as: maply-ml-services:$VERSION and maply-ml-services:latest"

# Show image info
echo ""
echo "📊 Image Information:"
docker images maply-ml-services:latest

echo ""
echo "🚀 To run the container:"
echo "   docker run -p 8000:8000 maply-ml-services:latest"
echo ""
echo "   Or use docker-compose:"
echo "   docker-compose up"
