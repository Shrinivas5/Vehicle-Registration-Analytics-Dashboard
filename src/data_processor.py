import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

class VahanDataProcessor:
    """
    Process and analyze vehicle registration data
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_yoy_growth(self, df: pd.DataFrame, group_cols: List[str]) -> pd.DataFrame:
        """
        Calculate Year-over-Year growth rates
        
        Args:
            df: DataFrame with vehicle registration data
            group_cols: Columns to group by (e.g., ['vehicle_type', 'manufacturer'])
        
        Returns:
            DataFrame with YoY growth calculations
        """
        # Group by specified columns and year, sum registrations
        yearly_data = df.groupby(group_cols + ['year'])['registrations'].sum().reset_index()
        
        # Calculate YoY growth
        yearly_data = yearly_data.sort_values(group_cols + ['year'])
        yearly_data['prev_year_registrations'] = yearly_data.groupby(group_cols)['registrations'].shift(1)
        yearly_data['yoy_growth'] = ((yearly_data['registrations'] - yearly_data['prev_year_registrations']) / 
                                    yearly_data['prev_year_registrations'] * 100).round(2)
        
        return yearly_data
    
    def calculate_qoq_growth(self, df: pd.DataFrame, group_cols: List[str]) -> pd.DataFrame:
        """
        Calculate Quarter-over-Quarter growth rates
        
        Args:
            df: DataFrame with vehicle registration data
            group_cols: Columns to group by
        
        Returns:
            DataFrame with QoQ growth calculations
        """
        # Create a period column for proper sorting
        df['period'] = df['year'].astype(str) + '-' + df['quarter']
        
        # Group by specified columns and period, sum registrations
        quarterly_data = df.groupby(group_cols + ['year', 'quarter', 'period'])['registrations'].sum().reset_index()
        
        # Sort by group columns and period
        quarterly_data = quarterly_data.sort_values(group_cols + ['year', 'quarter'])
        
        # Calculate QoQ growth
        quarterly_data['prev_quarter_registrations'] = quarterly_data.groupby(group_cols)['registrations'].shift(1)
        quarterly_data['qoq_growth'] = ((quarterly_data['registrations'] - quarterly_data['prev_quarter_registrations']) / 
                                       quarterly_data['prev_quarter_registrations'] * 100).round(2)
        
        return quarterly_data
    
    def get_top_manufacturers(self, df: pd.DataFrame, vehicle_type: str, n: int = 10) -> pd.DataFrame:
        """
        Get top N manufacturers by total registrations for a vehicle type
        
        Args:
            df: DataFrame with vehicle registration data
            vehicle_type: Vehicle type to filter (2W, 3W, 4W)
            n: Number of top manufacturers to return
        
        Returns:
            DataFrame with top manufacturers
        """
        filtered_df = df[df['vehicle_type'] == vehicle_type]
        top_manufacturers = (filtered_df.groupby('manufacturer')['registrations']
                           .sum()
                           .sort_values(ascending=False)
                           .head(n)
                           .reset_index())
        
        return top_manufacturers
    
    def get_market_share(self, df: pd.DataFrame, vehicle_type: str) -> pd.DataFrame:
        """
        Calculate market share for manufacturers in a vehicle category
        
        Args:
            df: DataFrame with vehicle registration data
            vehicle_type: Vehicle type to analyze
        
        Returns:
            DataFrame with market share calculations
        """
        filtered_df = df[df['vehicle_type'] == vehicle_type]
        
        # Calculate total registrations by manufacturer
        manufacturer_totals = filtered_df.groupby('manufacturer')['registrations'].sum().reset_index()
        
        # Calculate total market size
        total_market = manufacturer_totals['registrations'].sum()
        
        # Calculate market share
        manufacturer_totals['market_share'] = (manufacturer_totals['registrations'] / total_market * 100).round(2)
        manufacturer_totals = manufacturer_totals.sort_values('market_share', ascending=False)
        
        return manufacturer_totals
    
    def get_trend_analysis(self, df: pd.DataFrame) -> Dict:
        """
        Perform comprehensive trend analysis
        
        Args:
            df: DataFrame with vehicle registration data
        
        Returns:
            Dictionary with trend analysis results
        """
        analysis = {}
        
        # Overall vehicle type trends
        vehicle_trends = df.groupby(['year', 'vehicle_type'])['registrations'].sum().reset_index()
        analysis['vehicle_type_trends'] = vehicle_trends
        
        # Year-over-year growth by vehicle type
        yoy_vehicle = self.calculate_yoy_growth(df, ['vehicle_type'])
        analysis['yoy_by_vehicle_type'] = yoy_vehicle
        
        # Quarter-over-quarter growth by vehicle type
        qoq_vehicle = self.calculate_qoq_growth(df, ['vehicle_type'])
        analysis['qoq_by_vehicle_type'] = qoq_vehicle
        
        # Top performers analysis
        analysis['top_2w_manufacturers'] = self.get_top_manufacturers(df, '2W', 5)
        analysis['top_4w_manufacturers'] = self.get_top_manufacturers(df, '4W', 5)
        analysis['top_3w_manufacturers'] = self.get_top_manufacturers(df, '3W', 5)
        
        # Market share analysis
        analysis['market_share_2w'] = self.get_market_share(df, '2W')
        analysis['market_share_4w'] = self.get_market_share(df, '4W')
        analysis['market_share_3w'] = self.get_market_share(df, '3W')
        
        return analysis
