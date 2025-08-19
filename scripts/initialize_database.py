#!/usr/bin/env python3
"""
Initialize the Vahan Dashboard database with sample data and analytics
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.data_collector import VahanDataCollector
from src.database_manager import VahanDatabaseManager
import pandas as pd

def main():
    print("Initializing Vahan Dashboard Database...")
    
    # Initialize components
    collector = VahanDataCollector()
    db_manager = VahanDatabaseManager()
    
    # Fetch real data
    print("Fetching real vehicle registration data up to today...")
    df = collector.collect_all_data_up_to_today()
    
    # Generate sample data
    print("Generating comprehensive vehicle registration data...")
    df = collector.generate_sample_data()
    
    # Insert registration data
    print("Inserting registration data...")
    db_manager.bulk_insert_registrations(df)
    
    # Calculate analytics
    print("Calculating growth metrics...")
    db_manager.calculate_and_store_growth_metrics()
    
    print("Calculating market share data...")
    db_manager.calculate_and_store_market_share()
    
    # Print comprehensive stats
    stats = db_manager.get_database_stats()
    print(f"\n{'='*50}")
    print("DATABASE INITIALIZATION COMPLETE")
    print(f"{'='*50}")
    print(f"Total registration records: {stats['total_registrations']:,}")
    print(f"Total manufacturers: {stats['total_manufacturers']}")
    print(f"Date range: {stats['date_range'][0]} to {stats['date_range'][1]}")
    print(f"Growth metrics calculated: {stats['growth_metrics_count']:,}")
    print(f"Market share records: {stats['market_share_records']:,}")
    
    print(f"\nVehicle Type Distribution:")
    for vt in stats['vehicle_type_distribution']:
        print(f"  {vt['vehicle_type']}: {vt['total_registrations']:,} registrations ({vt['records']} records)")
    
    print(f"\n{'='*50}")
    print("Ready for dashboard development!")

if __name__ == "__main__":
    main()
