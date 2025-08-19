#!/bin/bash

# Setup script for Vahan Dashboard

echo "Setting up Vehicle Registration Analytics Dashboard..."

# Create necessary directories
mkdir -p data
mkdir -p logs

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Initialize database with sample data
echo "Initializing database..."
python scripts/initialize_database.py

# Run analytics to populate metrics
echo "Running analytics calculations..."
python scripts/run_analytics.py

echo "Setup complete!"
echo ""
echo "To start the dashboard, run:"
echo "python run_dashboard.py"
echo ""
echo "The dashboard will be available at: http://localhost:8501"
