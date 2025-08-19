import sqlite3
import pandas as pd
from typing import Optional
import logging

class VahanDatabase:
    """
    Database manager for vehicle registration data
    """
    
    def __init__(self, db_path: str = "data/vahan_data.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for better query performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON vehicle_registrations(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_vehicle_type ON vehicle_registrations(vehicle_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_manufacturer ON vehicle_registrations(manufacturer)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_year_quarter ON vehicle_registrations(year, quarter)')
        
        conn.commit()
        conn.close()
        
        self.logger.info("Database initialized successfully")
    
    def insert_data(self, df: pd.DataFrame):
        """Insert DataFrame into database"""
        conn = sqlite3.connect(self.db_path)
        
        # Clear existing data
        cursor = conn.cursor()
        cursor.execute('DELETE FROM vehicle_registrations')
        
        # Insert new data
        df.to_sql('vehicle_registrations', conn, if_exists='append', index=False)
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Inserted {len(df)} records into database")
    
    def get_data(self, 
                 start_date: Optional[str] = None,
                 end_date: Optional[str] = None,
                 vehicle_types: Optional[list] = None,
                 manufacturers: Optional[list] = None) -> pd.DataFrame:
        """
        Retrieve data from database with optional filters
        
        Args:
            start_date: Start date filter (YYYY-MM-DD)
            end_date: End date filter (YYYY-MM-DD)
            vehicle_types: List of vehicle types to filter
            manufacturers: List of manufacturers to filter
        
        Returns:
            Filtered DataFrame
        """
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT * FROM vehicle_registrations WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        if vehicle_types:
            placeholders = ','.join(['?' for _ in vehicle_types])
            query += f" AND vehicle_type IN ({placeholders})"
            params.extend(vehicle_types)
        
        if manufacturers:
            placeholders = ','.join(['?' for _ in manufacturers])
            query += f" AND manufacturer IN ({placeholders})"
            params.extend(manufacturers)
        
        query += " ORDER BY date, vehicle_type, manufacturer"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return df
    
    def get_summary_stats(self) -> dict:
        """Get summary statistics from database"""
        conn = sqlite3.connect(self.db_path)
        
        stats = {}
        
        # Total records
        stats['total_records'] = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM vehicle_registrations", conn
        ).iloc[0]['count']
        
        # Date range
        date_range = pd.read_sql_query(
            "SELECT MIN(date) as min_date, MAX(date) as max_date FROM vehicle_registrations", conn
        ).iloc[0]
        stats['date_range'] = (date_range['min_date'], date_range['max_date'])
        
        # Vehicle types
        stats['vehicle_types'] = pd.read_sql_query(
            "SELECT DISTINCT vehicle_type FROM vehicle_registrations ORDER BY vehicle_type", conn
        )['vehicle_type'].tolist()
        
        # Manufacturers count
        stats['total_manufacturers'] = pd.read_sql_query(
            "SELECT COUNT(DISTINCT manufacturer) as count FROM vehicle_registrations", conn
        ).iloc[0]['count']
        
        conn.close()
        return stats