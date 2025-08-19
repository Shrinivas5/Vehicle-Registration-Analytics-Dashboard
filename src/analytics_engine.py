import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

class GrowthPeriod(Enum):
    YOY = "yoy"
    QOQ = "qoq"
    MOM = "mom"

class VehicleCategory(Enum):
    TWO_WHEELER = "2W"
    THREE_WHEELER = "3W"
    FOUR_WHEELER = "4W"

@dataclass
class GrowthMetric:
    entity: str
    period: str
    current_value: int
    previous_value: int
    growth_rate: float
    growth_absolute: int
    rank: int

@dataclass
class MarketInsight:
    insight_type: str
    title: str
    description: str
    impact_level: str  # High, Medium, Low
    data_points: Dict
    recommendation: str

class VahanAnalyticsEngine:
    """
    Advanced analytics engine for vehicle registration data
    Focused on investor insights and market intelligence
    """
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
    
    def calculate_growth_metrics(self, 
                                df: pd.DataFrame, 
                                period_type: GrowthPeriod,
                                group_by: List[str]) -> List[GrowthMetric]:
        """
        Calculate growth metrics for specified period and grouping
        
        Args:
            df: DataFrame with registration data
            period_type: Type of growth calculation (YoY, QoQ, MoM)
            group_by: Columns to group by
        
        Returns:
            List of GrowthMetric objects
        """
        metrics = []
        
        if period_type == GrowthPeriod.YOY:
            # Year-over-year calculation
            yearly_data = df.groupby(group_by + ['year'])['registrations'].sum().reset_index()
            yearly_data = yearly_data.sort_values(group_by + ['year'])
            
            for group_vals in yearly_data[group_by].drop_duplicates().values:
                group_filter = True
                for i, col in enumerate(group_by):
                    group_filter &= (yearly_data[col] == group_vals[i])
                
                group_data = yearly_data[group_filter].sort_values('year')
                
                for idx in range(1, len(group_data)):
                    current = group_data.iloc[idx]
                    previous = group_data.iloc[idx-1]
                    
                    if previous['registrations'] > 0:
                        growth_rate = ((current['registrations'] - previous['registrations']) / 
                                     previous['registrations'] * 100)
                        
                        entity_name = ' - '.join([str(group_vals[i]) for i in range(len(group_by))])
                        
                        metrics.append(GrowthMetric(
                            entity=entity_name,
                            period=str(current['year']),
                            current_value=current['registrations'],
                            previous_value=previous['registrations'],
                            growth_rate=round(growth_rate, 2),
                            growth_absolute=current['registrations'] - previous['registrations'],
                            rank=0  # Will be calculated later
                        ))
        
        elif period_type == GrowthPeriod.QOQ:
            # Quarter-over-quarter calculation
            df['period_sort'] = df['year'] * 10 + df['quarter'].str[1].astype(int)
            quarterly_data = df.groupby(group_by + ['year', 'quarter', 'period_sort'])['registrations'].sum().reset_index()
            quarterly_data = quarterly_data.sort_values(group_by + ['period_sort'])
            
            for group_vals in quarterly_data[group_by].drop_duplicates().values:
                group_filter = True
                for i, col in enumerate(group_by):
                    group_filter &= (quarterly_data[col] == group_vals[i])
                
                group_data = quarterly_data[group_filter].sort_values('period_sort')
                
                for idx in range(1, len(group_data)):
                    current = group_data.iloc[idx]
                    previous = group_data.iloc[idx-1]
                    
                    if previous['registrations'] > 0:
                        growth_rate = ((current['registrations'] - previous['registrations']) / 
                                     previous['registrations'] * 100)
                        
                        entity_name = ' - '.join([str(group_vals[i]) for i in range(len(group_by))])
                        period_name = f"{current['year']}-{current['quarter']}"
                        
                        metrics.append(GrowthMetric(
                            entity=entity_name,
                            period=period_name,
                            current_value=current['registrations'],
                            previous_value=previous['registrations'],
                            growth_rate=round(growth_rate, 2),
                            growth_absolute=current['registrations'] - previous['registrations'],
                            rank=0
                        ))
        
        # Rank metrics by growth rate
        metrics.sort(key=lambda x: x.growth_rate, reverse=True)
        for i, metric in enumerate(metrics):
            metric.rank = i + 1
        
        return metrics
    
    def identify_market_leaders(self, df: pd.DataFrame, vehicle_type: str) -> Dict:
        """
        Identify market leaders and their competitive positioning
        
        Args:
            df: DataFrame with registration data
            vehicle_type: Vehicle category to analyze
        
        Returns:
            Dictionary with market leadership analysis
        """
        vehicle_data = df[df['vehicle_type'] == vehicle_type]
        
        # Calculate market share by manufacturer
        total_registrations = vehicle_data['registrations'].sum()
        market_share = (vehicle_data.groupby('manufacturer')['registrations']
                       .sum()
                       .sort_values(ascending=False))
        
        market_share_pct = (market_share / total_registrations * 100).round(2)
        
        # Identify market concentration (HHI - Herfindahl-Hirschman Index)
        hhi = (market_share_pct ** 2).sum()
        
        # Market structure analysis
        if hhi > 2500:
            market_structure = "Highly Concentrated"
        elif hhi > 1500:
            market_structure = "Moderately Concentrated"
        else:
            market_structure = "Competitive"
        
        # Top 3 players
        top_3 = market_share_pct.head(3)
        top_3_share = top_3.sum()
        
        return {
            'vehicle_type': vehicle_type,
            'market_leader': market_share_pct.index[0],
            'leader_share': market_share_pct.iloc[0],
            'top_3_players': top_3.to_dict(),
            'top_3_combined_share': top_3_share,
            'hhi_index': round(hhi, 2),
            'market_structure': market_structure,
            'total_players': len(market_share_pct),
            'fragmentation_level': 'High' if len(market_share_pct) > 15 else 'Medium' if len(market_share_pct) > 8 else 'Low'
        }
    
    def detect_growth_trends(self, df: pd.DataFrame) -> List[MarketInsight]:
        """
        Detect significant growth trends and patterns
        
        Args:
            df: DataFrame with registration data
        
        Returns:
            List of market insights
        """
        insights = []
        
        # Trend 1: Electric vehicle adoption
        if 'fuel_type' in df.columns:
            ev_data = df[df['fuel_type'] == 'Electric']
            if not ev_data.empty:
                ev_growth = ev_data.groupby('year')['registrations'].sum()
                if len(ev_growth) > 1:
                    latest_growth = ((ev_growth.iloc[-1] - ev_growth.iloc[-2]) / ev_growth.iloc[-2] * 100)
                    
                    if latest_growth > 50:
                        insights.append(MarketInsight(
                            insight_type="Growth Trend",
                            title="Electric Vehicle Surge",
                            description=f"Electric vehicle registrations grew by {latest_growth:.1f}% YoY, indicating rapid adoption",
                            impact_level="High",
                            data_points={
                                'growth_rate': latest_growth,
                                'current_registrations': ev_growth.iloc[-1],
                                'previous_registrations': ev_growth.iloc[-2]
                            },
                            recommendation="Consider investing in EV manufacturers and charging infrastructure"
                        ))
        
        # Trend 2: Market share shifts
        for vehicle_type in ['2W', '3W', '4W']:
            vehicle_data = df[df['vehicle_type'] == vehicle_type]
            yearly_manufacturer = (vehicle_data.groupby(['year', 'manufacturer'])['registrations']
                                 .sum().reset_index())
            
            # Calculate market share changes
            for year in yearly_manufacturer['year'].unique()[1:]:  # Skip first year
                current_year = yearly_manufacturer[yearly_manufacturer['year'] == year]
                previous_year = yearly_manufacturer[yearly_manufacturer['year'] == year - 1]
                
                current_total = current_year['registrations'].sum()
                previous_total = previous_year['registrations'].sum()
                
                for _, manufacturer_data in current_year.iterrows():
                    manufacturer = manufacturer_data['manufacturer']
                    current_share = manufacturer_data['registrations'] / current_total * 100
                    
                    prev_data = previous_year[previous_year['manufacturer'] == manufacturer]
                    if not prev_data.empty:
                        previous_share = prev_data.iloc[0]['registrations'] / previous_total * 100
                        share_change = current_share - previous_share
                        
                        if abs(share_change) > 2:  # Significant market share change
                            insights.append(MarketInsight(
                                insight_type="Market Share Shift",
                                title=f"{manufacturer} Market Position Change",
                                description=f"{manufacturer} {'gained' if share_change > 0 else 'lost'} {abs(share_change):.1f}% market share in {vehicle_type} segment",
                                impact_level="Medium" if abs(share_change) < 5 else "High",
                                data_points={
                                    'manufacturer': manufacturer,
                                    'vehicle_type': vehicle_type,
                                    'share_change': share_change,
                                    'current_share': current_share,
                                    'previous_share': previous_share
                                },
                                recommendation=f"{'Monitor for continued growth' if share_change > 0 else 'Investigate causes of decline'}"
                            ))
        
        # Trend 3: Seasonal patterns
        if 'quarter' in df.columns:
            quarterly_totals = df.groupby(['year', 'quarter'])['registrations'].sum().reset_index()
            quarterly_avg = quarterly_totals.groupby('quarter')['registrations'].mean()
            
            peak_quarter = quarterly_avg.idxmax()
            low_quarter = quarterly_avg.idxmin()
            seasonality_strength = (quarterly_avg.max() - quarterly_avg.min()) / quarterly_avg.mean() * 100
            
            if seasonality_strength > 20:
                insights.append(MarketInsight(
                    insight_type="Seasonal Pattern",
                    title="Strong Seasonal Demand Pattern",
                    description=f"Vehicle registrations show {seasonality_strength:.1f}% seasonal variation, peaking in {peak_quarter}",
                    impact_level="Medium",
                    data_points={
                        'peak_quarter': peak_quarter,
                        'low_quarter': low_quarter,
                        'seasonality_strength': seasonality_strength,
                        'quarterly_averages': quarterly_avg.to_dict()
                    },
                    recommendation="Plan inventory and marketing campaigns around seasonal patterns"
                ))
        
        return insights
    
    def calculate_market_concentration(self, df: pd.DataFrame) -> Dict:
        """
        Calculate market concentration metrics for investment analysis
        
        Args:
            df: DataFrame with registration data
        
        Returns:
            Dictionary with concentration metrics
        """
        concentration_metrics = {}
        
        for vehicle_type in df['vehicle_type'].unique():
            vehicle_data = df[df['vehicle_type'] == vehicle_type]
            
            # Market share calculation
            manufacturer_totals = vehicle_data.groupby('manufacturer')['registrations'].sum()
            total_market = manufacturer_totals.sum()
            market_shares = (manufacturer_totals / total_market * 100).sort_values(ascending=False)
            
            # Concentration ratios
            cr4 = market_shares.head(4).sum()  # Top 4 concentration ratio
            cr8 = market_shares.head(8).sum()  # Top 8 concentration ratio
            
            # Herfindahl-Hirschman Index
            hhi = (market_shares ** 2).sum()
            
            # Number of effective competitors
            effective_competitors = 1 / (hhi / 10000) if hhi > 0 else 0
            
            concentration_metrics[vehicle_type] = {
                'total_manufacturers': len(market_shares),
                'market_leader': market_shares.index[0],
                'leader_share': market_shares.iloc[0],
                'cr4_ratio': cr4,
                'cr8_ratio': cr8,
                'hhi_index': hhi,
                'effective_competitors': effective_competitors,
                'market_structure': self._classify_market_structure(hhi),
                'top_5_shares': market_shares.head(5).to_dict()
            }
        
        return concentration_metrics
    
    def _classify_market_structure(self, hhi: float) -> str:
        """Classify market structure based on HHI"""
        if hhi > 2500:
            return "Highly Concentrated (Oligopoly)"
        elif hhi > 1500:
            return "Moderately Concentrated"
        elif hhi > 1000:
            return "Unconcentrated (Competitive)"
        else:
            return "Highly Competitive"
    
    def generate_investment_scorecard(self, df: pd.DataFrame) -> Dict:
        """
        Generate investment attractiveness scorecard
        
        Args:
            df: DataFrame with registration data
        
        Returns:
            Investment scorecard with scores and recommendations
        """
        scorecard = {}
        
        for vehicle_type in df['vehicle_type'].unique():
            vehicle_data = df[df['vehicle_type'] == vehicle_type]
            
            # Growth momentum score (0-100)
            yoy_metrics = self.calculate_growth_metrics(vehicle_data, GrowthPeriod.YOY, ['manufacturer'])
            avg_growth = np.mean([m.growth_rate for m in yoy_metrics if m.growth_rate is not None])
            growth_score = min(100, max(0, (avg_growth + 20) * 2))  # Normalize to 0-100
            
            # Market size score
            total_registrations = vehicle_data['registrations'].sum()
            size_percentile = 33 if vehicle_type == '3W' else 67 if vehicle_type == '2W' else 100
            
            # Competition intensity score (inverse of concentration)
            concentration = self.calculate_market_concentration(vehicle_data)
            competition_score = max(0, 100 - concentration[vehicle_type]['hhi_index'] / 50)
            
            # Innovation score (based on fuel type diversity if available)
            innovation_score = 50  # Default
            if 'fuel_type' in vehicle_data.columns:
                fuel_diversity = len(vehicle_data['fuel_type'].unique())
                innovation_score = min(100, fuel_diversity * 20)
            
            # Overall investment attractiveness
            overall_score = (growth_score * 0.4 + size_percentile * 0.3 + 
                           competition_score * 0.2 + innovation_score * 0.1)
            
            # Investment recommendation
            if overall_score >= 75:
                recommendation = "Strong Buy - High growth potential with favorable market dynamics"
            elif overall_score >= 60:
                recommendation = "Buy - Positive outlook with moderate risk"
            elif overall_score >= 40:
                recommendation = "Hold - Mixed signals, monitor closely"
            else:
                recommendation = "Avoid - Challenging market conditions"
            
            scorecard[vehicle_type] = {
                'overall_score': round(overall_score, 1),
                'growth_momentum': round(growth_score, 1),
                'market_size': size_percentile,
                'competition_intensity': round(competition_score, 1),
                'innovation_potential': round(innovation_score, 1),
                'recommendation': recommendation,
                'key_metrics': {
                    'avg_yoy_growth': round(avg_growth, 2),
                    'total_market_size': total_registrations,
                    'number_of_players': concentration[vehicle_type]['total_manufacturers'],
                    'market_leader': concentration[vehicle_type]['market_leader']
                }
            }
        
        return scorecard
    
    def forecast_registrations(self, df: pd.DataFrame, periods: int = 4) -> Dict:
        """
        Simple trend-based forecasting for vehicle registrations
        
        Args:
            df: DataFrame with historical data
            periods: Number of future periods to forecast
        
        Returns:
            Dictionary with forecasts by vehicle type
        """
        forecasts = {}
        
        for vehicle_type in df['vehicle_type'].unique():
            vehicle_data = df[df['vehicle_type'] == vehicle_type]
            
            # Aggregate by year-quarter
            quarterly_data = (vehicle_data.groupby(['year', 'quarter'])['registrations']
                            .sum().reset_index())
            quarterly_data['period'] = (quarterly_data['year'] - quarterly_data['year'].min()) * 4 + \
                                     quarterly_data['quarter'].str[1].astype(int) - 1
            
            # Simple linear trend
            if len(quarterly_data) >= 4:
                x = quarterly_data['period'].values
                y = quarterly_data['registrations'].values
                
                # Linear regression
                coeffs = np.polyfit(x, y, 1)
                trend_slope = coeffs[0]
                intercept = coeffs[1]
                
                # Generate forecasts
                last_period = x[-1]
                forecast_periods = range(last_period + 1, last_period + periods + 1)
                forecast_values = [trend_slope * p + intercept for p in forecast_periods]
                
                # Calculate confidence based on historical volatility
                residuals = y - (trend_slope * x + intercept)
                std_error = np.std(residuals)
                
                forecasts[vehicle_type] = {
                    'forecast_values': [max(0, int(v)) for v in forecast_values],
                    'trend_slope': trend_slope,
                    'confidence_interval': std_error * 1.96,  # 95% confidence
                    'last_actual': int(y[-1]),
                    'growth_trend': 'Positive' if trend_slope > 0 else 'Negative'
                }
        
        return forecasts
