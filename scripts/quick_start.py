#!/usr/bin/env python3
"""
Quick start script for Vahan Dashboard
This script sets up the project and runs initial data collection
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def create_directories():
    """Create necessary directories"""
    directories = ['data', 'logs', 'exports']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Created project directories")

def setup_database():
    """Initialize SQLite database"""
    db_path = 'data/vahan_data.db'
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vehicle_registrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        year INTEGER NOT NULL,
        quarter TEXT NOT NULL,
        month INTEGER NOT NULL,
        vehicle_type TEXT NOT NULL,
        manufacturer TEXT NOT NULL,
        registrations INTEGER NOT NULL,
        state TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_registrations_composite 
    ON vehicle_registrations(vehicle_type, manufacturer, year, quarter)
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

def install_requirements():
    """Install Python requirements"""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Requirements installed")
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        return False
    return True

def main():
    print("🚗 Setting up Vahan Dashboard Project...")
    print("=" * 50)
    
    # Create directories
    create_directories()
    
    # Install requirements
    if not install_requirements():
        return
    
    # Setup database
    setup_database()
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("\nNext steps:")
    print("1. Run: python scripts/setup_data.py")
    print("2. Run: streamlit run dashboard/main.py")
    print("3. Open browser to: http://localhost:8501")

if __name__ == "__main__":
    main()
