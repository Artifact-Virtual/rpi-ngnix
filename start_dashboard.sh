#!/bin/bash

echo "🚀 Starting ArtifactVirtual Security Dashboard..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️ Virtual environment not found. Running installation..."
    ./install_dashboard.sh
fi

# Activate virtual environment
source venv/bin/activate

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if services are running
if ! docker-compose ps | grep -q "Up"; then
    echo "⚠️ Services not running. Starting Docker Compose..."
    docker-compose up -d
fi

echo "🛡️ Launching Security Dashboard Suite..."
python3 dashboard_launcher.py
