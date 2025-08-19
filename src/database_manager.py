import sqlite3
import pandas as pd
from typing import Optional, List, Dict, Tuple
import logging
from datetime import datetime, timedelta
import os

class VahanDatabaseManager:
    """
    Enhanced database manager with analytics capabilities
    """
    
    def __init__(self, db_path: str = "data/vahan_data.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.init_database()
    
    def init_database(self):
        """Initialize database with comprehensive schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create vehicle_registrations table
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
        
        # Create growth_metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS growth_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_type TEXT NOT NULL,
                entity_name TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                period TEXT NOT NULL,
                current_value INTEGER,
                previous_value INTEGER,
                growth_rate REAL,
                growth_absolute INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create market_share table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_share (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                period TEXT NOT NULL,
                vehicle_type TEXT NOT NULL,
                manufacturer TEXT NOT NULL,
                registrations INTEGER NOT NULL,
                market_share_percent REAL NOT NULL,
                rank_position INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON vehicle_registrations(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_vehicle_type ON vehicle_registrations(vehicle_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_manufacturer ON vehicle_registrations(manufacturer)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_year_quarter ON vehicle_registrations(year, quarter)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_growth_metrics ON growth_metrics(entity_type, metric_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_market_share ON market_share(vehicle_type, period)')
        
        conn.commit()
        conn.close()
        
        self.logger.info("Database initialized with comprehensive schema")
    
    def bulk_insert_registrations(self, df: pd.DataFrame, replace: bool = True):
        """
        Bulk insert vehicle registration data with optimizations
        
        Args:
            df: DataFrame with registration data
            replace: Whether to replace existing data
        """
        conn = sqlite3.connect(self.db_path)
        
        if replace:
            conn.execute('DELETE FROM vehicle_registrations')
            self.logger.info("Cleared existing registration data")
        
        df_enhanced = df.copy()
        
        # Ensure month column exists
        if 'month' not in df_enhanced.columns:
            df_enhanced['month'] = pd.to_datetime(df_enhanced['date']).dt.month
        
        # Select only the columns that exist in the database schema
        required_columns = ['date', 'year', 'quarter', 'month', 'vehicle_type', 'manufacturer', 'registrations']
        df_final = df_enhanced[required_columns]
        
        # Insert data
        df_final.to_sql('vehicle_registrations', conn, if_exists='append', index=False)
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Inserted {len(df)} registration records")
    
    def get_data(self, 
                 start_date: Optional[str] = None,
                 end_date: Optional[str] = None,
                 vehicle_types: Optional[List[str]] = None,
                 manufacturers: Optional[List[str]] = None) -> pd.DataFrame:
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
        
        # Convert date column to datetime
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        
        return df
    
    def calculate_and_store_growth_metrics(self):
        """
        Calculate and store YoY and QoQ growth metrics
        """
        conn = sqlite3.connect(self.db_path)
        
        # Clear existing growth metrics
        conn.execute('DELETE FROM growth_metrics')
        
        # Calculate YoY growth by manufacturer
        yoy_manufacturer_query = """
        WITH yearly_data AS (
            SELECT 
                manufacturer,
                vehicle_type,
                year,
                SUM(registrations) as total_registrations
            FROM vehicle_registrations
            GROUP BY manufacturer, vehicle_type, year
        ),
        yoy_growth AS (
            SELECT 
                y1.manufacturer,
                y1.vehicle_type,
                y1.year,
                y1.total_registrations as current_value,
                y2.total_registrations as previous_value,
                CASE 
                    WHEN y2.total_registrations > 0 
                    THEN ROUND(((y1.total_registrations - y2.total_registrations) * 100.0 / y2.total_registrations), 2)
                    ELSE NULL 
                END as growth_rate,
                (y1.total_registrations - COALESCE(y2.total_registrations, 0)) as growth_absolute
            FROM yearly_data y1
            LEFT JOIN yearly_data y2 ON y1.manufacturer = y2.manufacturer 
                AND y1.vehicle_type = y2.vehicle_type 
                AND y1.year = y2.year + 1
        )
        INSERT INTO growth_metrics (entity_type, entity_name, metric_type, period, current_value, previous_value, growth_rate, growth_absolute)
        SELECT 
            'manufacturer',
            manufacturer || ' (' || vehicle_type || ')',
            'yoy',
            CAST(year AS TEXT),
            current_value,
            previous_value,
            growth_rate,
            growth_absolute
        FROM yoy_growth
        WHERE previous_value IS NOT NULL
        """
        
        conn.execute(yoy_manufacturer_query)
        
        # Calculate QoQ growth by manufacturer
        qoq_manufacturer_query = """
        WITH quarterly_data AS (
            SELECT 
                manufacturer,
                vehicle_type,
                year,
                quarter,
                (year || '-' || quarter) as period,
                SUM(registrations) as total_registrations,
                ROW_NUMBER() OVER (PARTITION BY manufacturer, vehicle_type ORDER BY year, quarter) as period_num
            FROM vehicle_registrations
            GROUP BY manufacturer, vehicle_type, year, quarter
        ),
        qoq_growth AS (
            SELECT 
                q1.manufacturer,
                q1.vehicle_type,
                q1.period,
                q1.total_registrations as current_value,
                q2.total_registrations as previous_value,
                CASE 
                    WHEN q2.total_registrations > 0 
                    THEN ROUND(((q1.total_registrations - q2.total_registrations) * 100.0 / q2.total_registrations), 2)
                    ELSE NULL 
                END as growth_rate,
                (q1.total_registrations - COALESCE(q2.total_registrations, 0)) as growth_absolute
            FROM quarterly_data q1
            LEFT JOIN quarterly_data q2 ON q1.manufacturer = q2.manufacturer 
                AND q1.vehicle_type = q2.vehicle_type 
                AND q1.period_num = q2.period_num + 1
        )
        INSERT INTO growth_metrics (entity_type, entity_name, metric_type, period, current_value, previous_value, growth_rate, growth_absolute)
        SELECT 
            'manufacturer',
            manufacturer || ' (' || vehicle_type || ')',
            'qoq',
            period,
            current_value,
            previous_value,
            growth_rate,
            growth_absolute
        FROM qoq_growth
        WHERE previous_value IS NOT NULL
        """
        
        conn.execute(qoq_manufacturer_query)
        
        # Calculate vehicle type level growth
        vehicle_type_yoy_query = """
        WITH yearly_vehicle_data AS (
            SELECT 
                vehicle_type,
                year,
                SUM(registrations) as total_registrations
            FROM vehicle_registrations
            GROUP BY vehicle_type, year
        ),
        vehicle_yoy_growth AS (
            SELECT 
                v1.vehicle_type,
                v1.year,
                v1.total_registrations as current_value,
                v2.total_registrations as previous_value,
                CASE 
                    WHEN v2.total_registrations > 0 
                    THEN ROUND(((v1.total_registrations - v2.total_registrations) * 100.0 / v2.total_registrations), 2)
                    ELSE NULL 
                END as growth_rate,
                (v1.total_registrations - COALESCE(v2.total_registrations, 0)) as growth_absolute
            FROM yearly_vehicle_data v1
            LEFT JOIN yearly_vehicle_data v2 ON v1.vehicle_type = v2.vehicle_type 
                AND v1.year = v2.year + 1
        )
        INSERT INTO growth_metrics (entity_type, entity_name, metric_type, period, current_value, previous_value, growth_rate, growth_absolute)
        SELECT 
            'vehicle_type',
            vehicle_type,
            'yoy',
            CAST(year AS TEXT),
            current_value,
            previous_value,
            growth_rate,
            growth_absolute
        FROM vehicle_yoy_growth
        WHERE previous_value IS NOT NULL
        """
        
        conn.execute(vehicle_type_yoy_query)
        
        conn.commit()
        conn.close()
        
        self.logger.info("Growth metrics calculated and stored")
    
    def calculate_and_store_market_share(self):
        """
        Calculate and store market share data
        """
        conn = sqlite3.connect(self.db_path)
        
        # Clear existing market share data
        conn.execute('DELETE FROM market_share')
        
        # Calculate quarterly market share
        market_share_query = """
        WITH quarterly_totals AS (
            SELECT 
                (year || '-' || quarter) as period,
                vehicle_type,
                manufacturer,
                SUM(registrations) as registrations
            FROM vehicle_registrations
            GROUP BY year, quarter, vehicle_type, manufacturer
        ),
        vehicle_type_totals AS (
            SELECT 
                period,
                vehicle_type,
                SUM(registrations) as total_registrations
            FROM quarterly_totals
            GROUP BY period, vehicle_type
        ),
        market_share_calc AS (
            SELECT 
                qt.period,
                qt.vehicle_type,
                qt.manufacturer,
                qt.registrations,
                ROUND((qt.registrations * 100.0 / vtt.total_registrations), 2) as market_share_percent,
                ROW_NUMBER() OVER (PARTITION BY qt.period, qt.vehicle_type ORDER BY qt.registrations DESC) as rank_position
            FROM quarterly_totals qt
            JOIN vehicle_type_totals vtt ON qt.period = vtt.period AND qt.vehicle_type = vtt.vehicle_type
        )
        INSERT INTO market_share (period, vehicle_type, manufacturer, registrations, market_share_percent, rank_position)
        SELECT period, vehicle_type, manufacturer, registrations, market_share_percent, rank_position
        FROM market_share_calc
        """
        
        conn.execute(market_share_query)
        
        conn.commit()
        conn.close()
        
        self.logger.info("Market share data calculated and stored")
    
    def get_analytics_data(self, 
                          metric_type: str = 'yoy',
                          entity_type: str = 'manufacturer',
                          vehicle_type: Optional[str] = None,
                          limit: int = 20) -> pd.DataFrame:
        """
        Get pre-calculated analytics data
        
        Args:
            metric_type: 'yoy' or 'qoq'
            entity_type: 'manufacturer' or 'vehicle_type'
            vehicle_type: Filter by vehicle type (2W, 3W, 4W)
            limit: Number of records to return
        
        Returns:
            DataFrame with analytics data
        """
        conn = sqlite3.connect(self.db_path)
        
        query = """
        SELECT * FROM growth_metrics 
        WHERE metric_type = ? AND entity_type = ?
        """
        params = [metric_type, entity_type]
        
        if vehicle_type and entity_type == 'manufacturer':
            query += " AND entity_name LIKE ?"
            params.append(f"%({vehicle_type})%")
        
        query += " ORDER BY ABS(growth_rate) DESC LIMIT ?"
        params.append(limit)
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return df
    
    def get_market_leaders(self, vehicle_type: str, period: Optional[str] = None) -> pd.DataFrame:
        """
        Get market leaders for a vehicle type
        
        Args:
            vehicle_type: Vehicle type to analyze
            period: Specific period (optional, gets latest if not provided)
        
        Returns:
            DataFrame with market leaders
        """
        conn = sqlite3.connect(self.db_path)
        
        if period:
            query = """
            SELECT * FROM market_share 
            WHERE vehicle_type = ? AND period = ?
            ORDER BY rank_position
            """
            params = [vehicle_type, period]
        else:
            query = """
            SELECT * FROM market_share 
            WHERE vehicle_type = ? AND period = (
                SELECT MAX(period) FROM market_share WHERE vehicle_type = ?
            )
            ORDER BY rank_position
            """
            params = [vehicle_type, vehicle_type]
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return df
    
    def get_database_stats(self) -> Dict:
        """Get comprehensive database statistics"""
        conn = sqlite3.connect(self.db_path)
        
        stats = {}
        
        # Basic counts
        stats['total_registrations'] = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM vehicle_registrations", conn
        ).iloc[0]['count']
        
        stats['total_manufacturers'] = pd.read_sql_query(
            "SELECT COUNT(DISTINCT manufacturer) as count FROM vehicle_registrations", conn
        ).iloc[0]['count']
        
        # Date range
        date_info = pd.read_sql_query(
            "SELECT MIN(date) as min_date, MAX(date) as max_date FROM vehicle_registrations", conn
        ).iloc[0]
        stats['date_range'] = (date_info['min_date'], date_info['max_date'])
        
        # Vehicle type distribution
        vehicle_dist = pd.read_sql_query(
            """SELECT vehicle_type, COUNT(*) as records, SUM(registrations) as total_registrations 
               FROM vehicle_registrations 
               GROUP BY vehicle_type 
               ORDER BY total_registrations DESC""", conn
        )
        stats['vehicle_type_distribution'] = vehicle_dist.to_dict('records')
        
        # Growth metrics count
        stats['growth_metrics_count'] = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM growth_metrics", conn
        ).iloc[0]['count']
        
        # Market share records
        stats['market_share_records'] = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM market_share", conn
        ).iloc[0]['count']
        
        conn.close()
        return stats
