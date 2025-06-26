#!/bin/bash

echo "🚀 Starting ArtifactVirtual.com Deployment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed."
    exit 1
fi

# Navigate to the correct directory
cd "$(dirname "$0")"

echo "📦 Building Landing Page..."
cd ../../frontend/landing_page/v2
npm install
npm run build

echo "🏗️ Building Docker containers..."
cd ../../../core/cert-nginx

# Create data directories if they don't exist
mkdir -p data/nginx
mkdir -p data/certbot/conf
mkdir -p data/certbot/www

echo "🔐 Setting up SSL certificates..."
chmod +x init-letsencrypt.sh

# Check if certificates already exist
if [ -d "data/certbot/conf/live/artifactvirtual.com" ]; then
    echo "ℹ️ SSL certificates already exist. Skipping certificate generation."
    echo "🚀 Starting services..."
    docker-compose up -d
else
    echo "🔐 Generating SSL certificates..."
    ./init-letsencrypt.sh
fi

echo "✅ Deployment complete!"
echo ""
echo "🌐 Your site is available at:"
echo "   - https://artifactvirtual.com"
echo "   - Health check: https://artifactvirtual.com/health"
echo ""
echo "📊 Monitor with:"
echo "   - docker-compose logs -f"
echo "   - docker-compose ps"
echo ""
echo "🔄 To update:"
echo "   - ./deploy.sh"
echo ""
