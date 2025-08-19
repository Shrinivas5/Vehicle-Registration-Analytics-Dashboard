#!/usr/bin/env python3
"""
Test script to verify connection to the Vahan Dashboard
URL: https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.data_collector import VahanDataCollector
from datetime import datetime, timedelta

def main():
    print("🚗 Testing Vahan Dashboard Connection")
    print("=" * 50)
    print(f"Target URL: https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml")
    print()
    
    # Initialize collector
    collector = VahanDataCollector()
    
    # Test basic connection
    print("1. Testing basic connection...")
    connection_ok = collector.test_vahan_connection()
    
    if connection_ok:
        print("✅ Connection successful!")
        
        # Test data fetching
        print("\n2. Testing data fetching...")
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        print(f"   Fetching data from {start_date} to {end_date}")
        
        # Try to fetch vehicle data
        vehicle_data = collector.get_vehicle_data(start_date, end_date)
        
        if vehicle_data:
            print("✅ Vehicle data fetched successfully!")
            print(f"   Data keys: {list(vehicle_data.keys())}")
        else:
            print("⚠️ No vehicle data returned (using sample data instead)")
        
        # Try to fetch manufacturer data
        manufacturer_data = collector.get_manufacturer_data(start_date, end_date, "2W")
        
        if manufacturer_data:
            print("✅ Manufacturer data fetched successfully!")
            print(f"   Data keys: {list(manufacturer_data.keys())}")
        else:
            print("⚠️ No manufacturer data returned (using sample data instead)")
            
    else:
        print("❌ Connection failed!")
        print("   The system will use sample data for development purposes.")
    
    print("\n" + "=" * 50)
    print("Note: If real data fetching fails, the system automatically")
    print("generates realistic sample data that follows the same structure")
    print("as the actual Vahan Dashboard data.")

if __name__ == "__main__":
    main()
