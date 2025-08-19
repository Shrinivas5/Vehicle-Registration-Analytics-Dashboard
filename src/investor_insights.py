import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
from .analytics_engine import GrowthPeriod

@dataclass
class InvestmentTheme:
    theme_name: str
    description: str
    supporting_data: Dict
    investment_thesis: str
    risk_factors: List[str]
    potential_returns: str

class InvestorInsightsGenerator:
    """
    Generate sophisticated investor insights from vehicle registration data
    """
    
    def __init__(self, analytics_engine):
        self.analytics_engine = analytics_engine
        self.logger = logging.getLogger(__name__)
    
    def generate_executive_summary(self, df: pd.DataFrame) -> Dict:
        """
        Generate executive summary for investors
        
        Args:
            df: DataFrame with registration data
        
        Returns:
            Executive summary with key insights
        """
        if df.empty:
            return {
                'market_overview': {
                    'total_registrations': "0",
                    'yoy_growth': "N/A",
                    'total_manufacturers': 0,
                    'dominant_category': "No data available",
                    'market_size_category': "No data available"
                },
                'key_highlights': ["No data available for the selected filters"],
                'investment_outlook': "No data available",
                'risk_assessment': ["No data available"]
            }
        
        # Overall market metrics
        total_registrations = df['registrations'].sum()
        total_manufacturers = df['manufacturer'].nunique()
        
        # Growth analysis
        latest_year = df['year'].max()
        current_year_data = df[df['year'] == latest_year]['registrations'].sum()
        previous_year_data = df[df['year'] == latest_year - 1]['registrations'].sum()
        
        yoy_growth = ((current_year_data - previous_year_data) / previous_year_data * 100) if previous_year_data > 0 else 0
        
        # Vehicle type breakdown
        vehicle_breakdown = df.groupby('vehicle_type')['registrations'].sum().sort_values(ascending=False)
        dominant_category = vehicle_breakdown.index[0] if not vehicle_breakdown.empty else "No data"
        
        # Market concentration
        concentration_metrics = self.analytics_engine.calculate_market_concentration(df)
        
        return {
            'market_overview': {
                'total_registrations': f"{total_registrations:,}",
                'yoy_growth': f"{yoy_growth:.1f}%",
                'total_manufacturers': total_manufacturers,
                'dominant_category': dominant_category,
                'market_size_category': self._classify_market_size(total_registrations)
            },
            'key_highlights': [
                f"Market grew {yoy_growth:.1f}% YoY with {total_registrations:,} total registrations",
                f"{dominant_category} segment dominates with {vehicle_breakdown.iloc[0] if not vehicle_breakdown.empty else 0:,} registrations",
                f"Market features {total_manufacturers} active manufacturers across all segments",
                f"Concentration varies by segment: {self._get_concentration_summary(concentration_metrics)}"
            ],
            'investment_outlook': self._generate_investment_outlook(df),
            'risk_assessment': self._assess_market_risks(df)
        }
    
    def identify_investment_themes(self, df: pd.DataFrame) -> List[InvestmentTheme]:
        """
        Identify key investment themes from the data
        
        Args:
            df: DataFrame with registration data
        
        Returns:
            List of investment themes
        """
        themes = []
        
        # Theme 1: Electric Vehicle Revolution
        if 'fuel_type' in df.columns:
            ev_data = df[df['fuel_type'] == 'Electric']
            if not ev_data.empty:
                ev_growth = ev_data.groupby('year')['registrations'].sum()
                if len(ev_growth) > 1:
                    ev_cagr = ((ev_growth.iloc[-1] / ev_growth.iloc[0]) ** (1/(len(ev_growth)-1)) - 1) * 100
                    
                    themes.append(InvestmentTheme(
                        theme_name="Electric Vehicle Adoption",
                        description="Rapid transition to electric mobility across vehicle segments",
                        supporting_data={
                            'ev_cagr': f"{ev_cagr:.1f}%",
                            'current_ev_registrations': ev_growth.iloc[-1],
                            'ev_market_share': f"{(ev_data['registrations'].sum() / df['registrations'].sum() * 100):.1f}%"
                        },
                        investment_thesis="Government incentives and environmental concerns driving massive shift to EVs",
                        risk_factors=[
                            "Charging infrastructure development lag",
                            "Battery technology and cost challenges",
                            "Policy changes affecting incentives"
                        ],
                        potential_returns="High (20-30% CAGR potential)"
                    ))
        
        # Theme 2: Market Consolidation
        concentration_metrics = self.analytics_engine.calculate_market_concentration(df)
        for vehicle_type, metrics in concentration_metrics.items():
            if metrics['hhi_index'] > 1500:  # Moderately to highly concentrated
                themes.append(InvestmentTheme(
                    theme_name=f"{vehicle_type} Market Consolidation",
                    description=f"Increasing concentration in {vehicle_type} segment favoring market leaders",
                    supporting_data={
                        'market_leader': metrics['market_leader'],
                        'leader_share': f"{metrics['leader_share']:.1f}%",
                        'top_4_share': f"{metrics['cr4_ratio']:.1f}%",
                        'hhi_index': metrics['hhi_index']
                    },
                    investment_thesis="Market leaders gaining pricing power and economies of scale",
                    risk_factors=[
                        "Regulatory intervention in concentrated markets",
                        "New entrant disruption",
                        "Technology shifts favoring smaller players"
                    ],
                    potential_returns="Medium-High (15-25% CAGR for leaders)"
                ))
        
        # Theme 3: Emerging Market Growth
        growth_metrics = self.analytics_engine.calculate_growth_metrics(df, GrowthPeriod.YOY, ['vehicle_type'])
        high_growth_segments = [m for m in growth_metrics if m.growth_rate > 15]
        
        if high_growth_segments:
            fastest_growing = max(high_growth_segments, key=lambda x: x.growth_rate)
            themes.append(InvestmentTheme(
                theme_name="High-Growth Segment Opportunity",
                description=f"Exceptional growth in {fastest_growing.entity} segment",
                supporting_data={
                    'growth_rate': f"{fastest_growing.growth_rate:.1f}%",
                    'current_registrations': fastest_growing.current_value,
                    'growth_absolute': fastest_growing.growth_absolute
                },
                investment_thesis="Structural demand drivers supporting sustained high growth",
                risk_factors=[
                    "Growth rate normalization as market matures",
                    "Increased competition as segment attracts entrants",
                    "Economic downturn impact on discretionary purchases"
                ],
                potential_returns="High (25-40% CAGR potential)"
            ))
        
        return themes
    
    def generate_competitive_analysis(self, df: pd.DataFrame, vehicle_type: str) -> Dict:
        """
        Generate detailed competitive analysis for a vehicle segment
        
        Args:
            df: DataFrame with registration data
            vehicle_type: Vehicle type to analyze
        
        Returns:
            Competitive analysis report
        """
        vehicle_data = df[df['vehicle_type'] == vehicle_type]
        
        # Market share analysis
        manufacturer_totals = vehicle_data.groupby('manufacturer')['registrations'].sum().sort_values(ascending=False)
        total_market = manufacturer_totals.sum()
        market_shares = (manufacturer_totals / total_market * 100).round(2)
        
        # Growth analysis by manufacturer
        yoy_metrics = self.analytics_engine.calculate_growth_metrics(
            vehicle_data, GrowthPeriod.YOY, ['manufacturer']
        )
        
        # Competitive positioning
        competitive_matrix = []
        for manufacturer in market_shares.index[:10]:  # Top 10 players
            manufacturer_growth = next((m.growth_rate for m in yoy_metrics if manufacturer in m.entity), 0)
            
            # Classify competitive position
            if market_shares[manufacturer] > 15 and manufacturer_growth > 10:
                position = "Star (High Share, High Growth)"
            elif market_shares[manufacturer] > 15 and manufacturer_growth <= 10:
                position = "Cash Cow (High Share, Low Growth)"
            elif market_shares[manufacturer] <= 15 and manufacturer_growth > 10:
                position = "Question Mark (Low Share, High Growth)"
            else:
                position = "Dog (Low Share, Low Growth)"
            
            competitive_matrix.append({
                'manufacturer': manufacturer,
                'market_share': market_shares[manufacturer],
                'yoy_growth': manufacturer_growth,
                'position': position,
                'registrations': manufacturer_totals[manufacturer]
            })
        
        return {
            'segment': vehicle_type,
            'market_size': total_market,
            'market_leader': market_shares.index[0],
            'leader_share': market_shares.iloc[0],
            'competitive_matrix': competitive_matrix,
            'market_dynamics': {
                'fragmentation_level': 'High' if len(market_shares) > 15 else 'Medium' if len(market_shares) > 8 else 'Low',
                'growth_leaders': [m['manufacturer'] for m in competitive_matrix if m['yoy_growth'] > 15],
                'market_share_leaders': market_shares.head(3).to_dict(),
                'emerging_players': [m['manufacturer'] for m in competitive_matrix if m['position'] == "Question Mark (Low Share, High Growth)"]
            }
        }
    
    def calculate_tam_sam_som(self, df: pd.DataFrame) -> Dict:
        """
        Calculate Total Addressable Market, Serviceable Addressable Market, and Serviceable Obtainable Market
        
        Args:
            df: DataFrame with registration data
        
        Returns:
            TAM/SAM/SOM analysis
        """
        # This is a simplified calculation - in reality, you'd use external market research
        current_registrations = df['registrations'].sum()
        
        # Assumptions for market sizing
        tam_multiplier = 3.0  # Assume current registrations represent 1/3 of total addressable market
        sam_multiplier = 2.0  # Serviceable addressable market
        som_percentage = 0.05  # Assume 5% serviceable obtainable market share
        
        tam = current_registrations * tam_multiplier
        sam = current_registrations * sam_multiplier
        som = sam * som_percentage
        
        return {
            'total_addressable_market': {
                'value': tam,
                'description': "Total market opportunity across all segments and regions"
            },
            'serviceable_addressable_market': {
                'value': sam,
                'description': "Market opportunity for products/services we can realistically serve"
            },
            'serviceable_obtainable_market': {
                'value': som,
                'description': "Realistic market share we can capture in near term"
            },
            'market_penetration': {
                'current_penetration': f"{(current_registrations / tam * 100):.1f}%",
                'growth_potential': f"{((sam - current_registrations) / current_registrations * 100):.0f}%"
            }
        }
    
    def _classify_market_size(self, total_registrations: int) -> str:
        """Classify market size"""
        if total_registrations > 10000000:
            return "Large Market (>10M registrations)"
        elif total_registrations > 1000000:
            return "Medium Market (1-10M registrations)"
        else:
            return "Small Market (<1M registrations)"
    
    def _get_concentration_summary(self, concentration_metrics: Dict) -> str:
        """Get summary of market concentration"""
        structures = [metrics['market_structure'] for metrics in concentration_metrics.values()]
        if all('Highly Concentrated' in s for s in structures):
            return "All segments highly concentrated"
        elif all('Competitive' in s for s in structures):
            return "All segments competitive"
        else:
            return "Mixed concentration levels across segments"
    
    def _generate_investment_outlook(self, df: pd.DataFrame) -> str:
        """Generate investment outlook"""
        scorecard = self.analytics_engine.generate_investment_scorecard(df)
        avg_score = np.mean([s['overall_score'] for s in scorecard.values()])
        
        if avg_score >= 75:
            return "Positive - Strong growth fundamentals with favorable market dynamics"
        elif avg_score >= 60:
            return "Cautiously Optimistic - Good opportunities with selective approach needed"
        elif avg_score >= 40:
            return "Neutral - Mixed signals requiring careful analysis"
        else:
            return "Cautious - Challenging market conditions with limited opportunities"
    
    def _assess_market_risks(self, df: pd.DataFrame) -> List[str]:
        """Assess key market risks"""
        risks = []
        
        # Check for high concentration risk
        concentration_metrics = self.analytics_engine.calculate_market_concentration(df)
        high_concentration_segments = [vt for vt, metrics in concentration_metrics.items() 
                                     if metrics['hhi_index'] > 2500]
        
        if high_concentration_segments:
            risks.append(f"High concentration risk in {', '.join(high_concentration_segments)} segments")
        
        # Check for declining segments
        yoy_metrics = self.analytics_engine.calculate_growth_metrics(df, GrowthPeriod.YOY, ['vehicle_type'])
        declining_segments = [m.entity for m in yoy_metrics if m.growth_rate < -5]
        
        if declining_segments:
            risks.append(f"Declining demand in {', '.join(declining_segments)}")
        
        # Add standard market risks
        risks.extend([
            "Economic downturn impact on vehicle purchases",
            "Regulatory changes affecting vehicle standards",
            "Technology disruption from new mobility solutions"
        ])
        
        return risks
