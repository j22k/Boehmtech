#!/bin/bash

# Boehm Tech TaskMaster Deployment Script
# This script sets up and runs the TaskMaster application

echo "🚀 Boehm Tech TaskMaster Deployment Script"
echo "=========================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p src/static/uploads
mkdir -p src/database

# Set permissions
chmod +x deploy.sh
chmod 755 src/static/uploads

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Default Admin Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "🌐 Starting the application..."
echo "   Access it at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the application
python src/main.py

