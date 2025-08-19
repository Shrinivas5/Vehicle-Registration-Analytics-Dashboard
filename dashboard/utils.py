"""
Utility functions for the dashboard
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

def format_number(num: int) -> str:
    """Format numbers with appropriate suffixes"""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return f"{num:,}"

def calculate_growth_rate(current: float, previous: float) -> float:
    """Calculate growth rate percentage"""
    if previous == 0:
        return 0
    return ((current - previous) / previous) * 100

def get_growth_indicator(growth_rate: float) -> Tuple[str, str]:
    """Get growth indicator symbol and CSS class"""
    if growth_rate > 0:
        return "↑", "positive"
    elif growth_rate < 0:
        return "↓", "negative"
    else:
        return "→", "neutral"

def filter_dataframe(df: pd.DataFrame, filters: Dict) -> pd.DataFrame:
    """Apply filters to dataframe"""
    filtered_df = df.copy()
    
    # Date range filter
    if 'date_range' in filters and filters['date_range']:
        start_date, end_date = filters['date_range']
        filtered_df = filtered_df[
            (pd.to_datetime(filtered_df['date']).dt.date >= start_date) &
            (pd.to_datetime(filtered_df['date']).dt.date <= end_date)
        ]
    
    # Vehicle type filter
    if 'vehicle_type' in filters and filters['vehicle_type'] != 'All':
        filtered_df = filtered_df[filtered_df['vehicle_type'] == filters['vehicle_type']]
    
    # Manufacturer filter
    if 'manufacturer' in filters and filters['manufacturer'] != 'All':
        filtered_df = filtered_df[filtered_df['manufacturer'] == filters['manufacturer']]
    
    return filtered_df

def get_period_comparison(df: pd.DataFrame, period_type: str = 'year') -> Dict:
    """Get period-over-period comparison"""
    if df.empty:
        return {}
    
    if period_type == 'year':
        current_period = df['year'].max()
        previous_period = current_period - 1
        
        current_data = df[df['year'] == current_period]['registrations'].sum()
        previous_data = df[df['year'] == previous_period]['registrations'].sum()
    
    elif period_type == 'quarter':
        # Get latest quarter
        df_sorted = df.sort_values(['year', 'quarter'])
        latest_record = df_sorted.iloc[-1]
        current_year, current_quarter = latest_record['year'], latest_record['quarter']
        
        # Calculate previous quarter
        if current_quarter == 'Q1':
            prev_year, prev_quarter = current_year - 1, 'Q4'
        else:
            prev_year = current_year
            prev_quarter = f"Q{int(current_quarter[1]) - 1}"
        
        current_data = df[
            (df['year'] == current_year) & (df['quarter'] == current_quarter)
        ]['registrations'].sum()
        
        previous_data = df[
            (df['year'] == prev_year) & (df['quarter'] == prev_quarter)
        ]['registrations'].sum()
    
    growth_rate = calculate_growth_rate(current_data, previous_data)
    symbol, css_class = get_growth_indicator(growth_rate)
    
    return {
        'current': current_data,
        'previous': previous_data,
        'growth_rate': growth_rate,
        'symbol': symbol,
        'css_class': css_class
    }

def validate_data(df: pd.DataFrame) -> List[str]:
    """Validate data quality and return issues"""
    issues = []
    
    if df.empty:
        issues.append("No data available")
        return issues
    
    # Check for required columns
    required_columns = ['date', 'year', 'quarter', 'vehicle_type', 'manufacturer', 'registrations']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        issues.append(f"Missing columns: {', '.join(missing_columns)}")
    
    # Check for null values in critical columns
    for col in ['registrations', 'vehicle_type', 'manufacturer']:
        if col in df.columns and df[col].isnull().any():
            issues.append(f"Null values found in {col}")
    
    # Check for negative registrations
    if 'registrations' in df.columns and (df['registrations'] < 0).any():
        issues.append("Negative registration values found")
    
    # Check date range
    if 'date' in df.columns:
        try:
            date_range = pd.to_datetime(df['date'])
            if date_range.max() < datetime.now() - timedelta(days=365):
                issues.append("Data appears to be outdated (older than 1 year)")
        except:
            issues.append("Invalid date format")
    
    return issues
