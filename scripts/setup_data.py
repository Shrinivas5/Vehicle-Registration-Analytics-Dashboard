#!/usr/bin/env python3
"""
Script to set up initial data for the Vahan Dashboard project
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.data_collector import VahanDataCollector
from src.database import VahanDatabase
import pandas as pd

def main():
    print("Setting up Vahan Dashboard data...")
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Initialize components
    collector = VahanDataCollector()
    db = VahanDatabase()
    
    # Generate sample data (replace with real API calls when available)
    print("Generating sample vehicle registration data...")
    df = collector.generate_sample_data()
    
    # Save to CSV
    collector.save_data(df, "vehicle_registrations.csv")
    
    # Insert into database
    print("Inserting data into database...")
    db.insert_data(df)
    
    # Print summary
    stats = db.get_summary_stats()
    print(f"\nData setup complete!")
    print(f"Total records: {stats['total_records']}")
    print(f"Date range: {stats['date_range'][0]} to {stats['date_range'][1]}")
    print(f"Vehicle types: {', '.join(stats['vehicle_types'])}")
    print(f"Total manufacturers: {stats['total_manufacturers']}")

if __name__ == "__main__":
    main()
