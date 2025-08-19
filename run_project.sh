#!/bin/bash
# Complete project execution script

echo "🚗 Starting Vahan Dashboard Setup..."
echo "=================================="

# Step 1: Setup project
echo "1. Setting up project structure..."
python scripts/quick_start.py

# Step 2: Generate data
echo "2. Generating sample data..."
python scripts/setup_data.py

# Step 3: Launch dashboard
echo "3. Launching dashboard..."
echo "Dashboard will be available at: http://localhost:8501"
streamlit run dashboard/main.py
