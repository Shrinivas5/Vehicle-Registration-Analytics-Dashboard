#!/bin/bash

# Vahan Dashboard Quick Start Script
# This script sets up the entire project and launches the dashboard

set -e  # Exit on any error

echo "🚀 Starting Vahan Dashboard Setup..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8+ required. Found: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p data logs database/migrations dashboard/assets

# Initialize database
echo "🗄️ Setting up database..."
python scripts/initialize_database.py

# Generate sample data (if no real data available)
echo "📊 Setting up sample data..."
python scripts/setup_data.py

# Run initial analytics
echo "🔍 Running initial analytics..."
python scripts/run_analytics.py

echo "✅ Setup complete!"
echo ""
echo "🎯 To start the dashboard:"
echo "   source venv/bin/activate"
echo "   streamlit run dashboard/main.py"
echo ""
echo "🌐 Dashboard will be available at: http://localhost:8501"
echo ""
echo "📹 Don't forget to record your 5-minute walkthrough video!"
