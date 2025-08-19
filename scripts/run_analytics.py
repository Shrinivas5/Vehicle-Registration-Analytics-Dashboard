#!/usr/bin/env python3
"""
Run comprehensive analytics on vehicle registration data
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.database_manager import VahanDatabaseManager
from src.analytics_engine import VahanAnalyticsEngine
from src.investor_insights import InvestorInsightsGenerator
import json

def main():
    print("Running Vahan Dashboard Analytics...")
    
    # Initialize components
    db_manager = VahanDatabaseManager()
    analytics_engine = VahanAnalyticsEngine(db_manager)
    insights_generator = InvestorInsightsGenerator(analytics_engine)
    
    # Get data
    df = db_manager.get_data()
    
    if df.empty:
        print("No data found. Please run initialize_database.py first.")
        return
    
    print(f"Analyzing {len(df)} registration records...")
    
    # Generate executive summary
    print("\n" + "="*60)
    print("EXECUTIVE SUMMARY")
    print("="*60)
    
    exec_summary = insights_generator.generate_executive_summary(df)
    
    print(f"Market Overview:")
    for key, value in exec_summary['market_overview'].items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print(f"\nKey Highlights:")
    for highlight in exec_summary['key_highlights']:
        print(f"  • {highlight}")
    
    print(f"\nInvestment Outlook: {exec_summary['investment_outlook']}")
    
    # Investment scorecard
    print("\n" + "="*60)
    print("INVESTMENT SCORECARD")
    print("="*60)
    
    scorecard = analytics_engine.generate_investment_scorecard(df)
    
    for vehicle_type, scores in scorecard.items():
        print(f"\n{vehicle_type} Segment:")
        print(f"  Overall Score: {scores['overall_score']}/100")
        print(f"  Recommendation: {scores['recommendation']}")
        print(f"  Growth Momentum: {scores['growth_momentum']}/100")
        print(f"  Market Leader: {scores['key_metrics']['market_leader']}")
        print(f"  YoY Growth: {scores['key_metrics']['avg_yoy_growth']:.1f}%")
    
    # Investment themes
    print("\n" + "="*60)
    print("INVESTMENT THEMES")
    print("="*60)
    
    themes = insights_generator.identify_investment_themes(df)
    
    for i, theme in enumerate(themes, 1):
        print(f"\n{i}. {theme.theme_name}")
        print(f"   Description: {theme.description}")
        print(f"   Investment Thesis: {theme.investment_thesis}")
        print(f"   Potential Returns: {theme.potential_returns}")
        print(f"   Key Data Points:")
        for key, value in theme.supporting_data.items():
            print(f"     • {key.replace('_', ' ').title()}: {value}")
    
    # Market concentration analysis
    print("\n" + "="*60)
    print("MARKET CONCENTRATION ANALYSIS")
    print("="*60)
    
    concentration = analytics_engine.calculate_market_concentration(df)
    
    for vehicle_type, metrics in concentration.items():
        print(f"\n{vehicle_type} Segment:")
        print(f"  Market Structure: {metrics['market_structure']}")
        print(f"  Market Leader: {metrics['market_leader']} ({metrics['leader_share']:.1f}%)")
        print(f"  Top 4 Concentration: {metrics['cr4_ratio']:.1f}%")
        print(f"  HHI Index: {metrics['hhi_index']:.0f}")
        print(f"  Total Players: {metrics['total_manufacturers']}")
    
    # Growth trends
    print("\n" + "="*60)
    print("GROWTH TRENDS & INSIGHTS")
    print("="*60)
    
    market_insights = analytics_engine.detect_growth_trends(df)
    
    for insight in market_insights:
        print(f"\n{insight.insight_type}: {insight.title}")
        print(f"  Impact Level: {insight.impact_level}")
        print(f"  Description: {insight.description}")
        print(f"  Recommendation: {insight.recommendation}")
    
    # Forecasting
    print("\n" + "="*60)
    print("MARKET FORECASTS")
    print("="*60)
    
    forecasts = analytics_engine.forecast_registrations(df, periods=4)
    
    for vehicle_type, forecast in forecasts.items():
        print(f"\n{vehicle_type} Forecast (Next 4 Quarters):")
        print(f"  Trend: {forecast['growth_trend']}")
        print(f"  Last Actual: {forecast['last_actual']:,}")
        print(f"  Forecasted Values: {[f'{v:,}' for v in forecast['forecast_values']]}")
        print(f"  Trend Slope: {forecast['trend_slope']:.0f} registrations per quarter")
    
    print(f"\n{'='*60}")
    print("ANALYTICS COMPLETE")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
