#!/bin/bash

echo "🛡️ Installing Security Dashboard Dependencies..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing dashboard requirements..."
pip install -r monitor_requirements.txt

echo "✅ Installation complete!"
echo ""
echo "🚀 To start the dashboard:"
echo "   source venv/bin/activate"
echo "   python3 dashboard_launcher.py"
echo ""
echo "Or run the quick start script:"
echo "   ./start_dashboard.sh"
