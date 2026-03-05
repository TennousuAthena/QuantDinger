#!/bin/bash
# QuantDinger Development Environment Startup Script
# This script starts the development environment with hot reload enabled

set -e

echo "🚀 Starting QuantDinger Development Environment..."
echo "   Hot reload enabled for both frontend and backend"
echo ""

# Check if .env file exists for backend
if [ ! -f "backend_api_python/.env" ]; then
    echo "⚠️  Warning: backend_api_python/.env not found"
    echo "   Creating from example..."
    if [ -f "backend_api_python/env.example" ]; then
        cp backend_api_python/env.example backend_api_python/.env
        echo "✅ Created backend_api_python/.env from example"
    fi
fi

# Create necessary directories
mkdir -p backend_api_python/logs backend_api_python/data

# Start development environment
echo ""
echo "📦 Starting Docker Compose (development mode)..."
docker compose -f docker-compose.dev.yml up --build

# Note: Use Ctrl+C to stop the services
