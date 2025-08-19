import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime, timedelta
import numpy as np

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.database_manager import VahanDatabaseManager
from src.analytics_engine import VahanAnalyticsEngine, GrowthPeriod
from src.investor_insights import InvestorInsightsGenerator

# Page configuration
st.set_page_config(
    page_title="Vehicle Registration Analytics Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with media queries and animations
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=DM+Sans:wght@400;500;600&display=swap');
    
    .main-header {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 2.5rem;
        color: #1f2937;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        font-family: 'DM Sans', sans-serif;
        font-size: 1.1rem;
        color: #6b7280;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #ffffff, #f8fafc);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 4px solid #8b5cf6;
        margin-bottom: 1rem;
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.1);
    }
    
    .metric-title {
        font-family: 'DM Sans', sans-serif;
        font-weight: 600;
        color: #374151;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 2rem;
        color: #1f2937;
    }
    
    .metric-change {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.85rem;
        margin-top: 0.25rem;
    }
    
    .positive { color: #059669; }
    .negative { color: #dc2626; }
    
    .section-header {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        font-size: 1.5rem;
        color: #1f2937;
        margin: 2rem 0 1rem 0;
        border-bottom: 2px solid #f1f5f9;
        padding-bottom: 0.5rem;
    }
    
    .insight-card {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #8b5cf6;
        margin: 1rem 0;
    }
    
    .insight-title {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    
    .insight-text {
        font-family: 'DM Sans', sans-serif;
        color: #4b5563;
        line-height: 1.6;
    }
    
    .sidebar .sidebar-content {
        background-color: #f8fafc;
    }
    
    .stSelectbox label {
        font-family: 'DM Sans', sans-serif;
        font-weight: 500;
        color: #374151;
    }
    
    # Responsive media queries
    @media (max-width: 768px) {
        .metric-card {
            padding: 1rem;
            font-size: 0.9rem;
        }
        .main-header {
            font-size: 1.8rem;
        }
        .st-columns > div {
            flex-direction: column;
        }
    }
</style>
""", unsafe_allow_html=True)

def load_data():
    """Load data from database"""
    try:
        # Fix database path to work from dashboard directory
        import os
        db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'vahan_data.db')
        db_manager = VahanDatabaseManager(db_path)
        df = db_manager.get_data()
        return df, db_manager
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), None

def get_analytics_components(df):
    """Initialize analytics components"""
    if df.empty:
        return None, None
    
    # Fix database path to work from dashboard directory
    import os
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'vahan_data.db')
    db_manager = VahanDatabaseManager(db_path)
    analytics_engine = VahanAnalyticsEngine(db_manager)
    insights_generator = InvestorInsightsGenerator(analytics_engine)
    
    return analytics_engine, insights_generator

def create_growth_chart(df, period_type="YoY"):
    """Create growth rate visualization"""
    if df.empty:
        return go.Figure()
    
    # Calculate growth by vehicle type
    if period_type == "YoY":
        growth_data = df.groupby(['year', 'vehicle_type'])['registrations'].sum().reset_index()
        growth_data = growth_data.sort_values(['vehicle_type', 'year'])
        
        # Calculate YoY growth
        growth_rates = []
        for vtype in growth_data['vehicle_type'].unique():
            vtype_data = growth_data[growth_data['vehicle_type'] == vtype].sort_values('year')
            for i in range(1, len(vtype_data)):
                current = vtype_data.iloc[i]['registrations']
                previous = vtype_data.iloc[i-1]['registrations']
                growth_rate = ((current - previous) / previous * 100) if previous > 0 else 0
                
                growth_rates.append({
                    'year': vtype_data.iloc[i]['year'],
                    'vehicle_type': vtype,
                    'growth_rate': growth_rate
                })
        
        growth_df = pd.DataFrame(growth_rates)
    else:  # QoQ
        growth_data = df.groupby(['year', 'quarter', 'vehicle_type'])['registrations'].sum().reset_index()
        growth_data['period'] = growth_data['year'].astype(str) + '-' + growth_data['quarter']
        growth_data = growth_data.sort_values(['vehicle_type', 'year', 'quarter'])
        
        growth_rates = []
        for vtype in growth_data['vehicle_type'].unique():
            vtype_data = growth_data[growth_data['vehicle_type'] == vtype].sort_values(['year', 'quarter'])
            for i in range(1, len(vtype_data)):
                current = vtype_data.iloc[i]['registrations']
                previous = vtype_data.iloc[i-1]['registrations']
                growth_rate = ((current - previous) / previous * 100) if previous > 0 else 0
                
                growth_rates.append({
                    'period': vtype_data.iloc[i]['period'],
                    'vehicle_type': vtype,
                    'growth_rate': growth_rate
                })
        
        growth_df = pd.DataFrame(growth_rates)
    
    if growth_df.empty:
        return go.Figure()
    
    # Create the chart
    fig = px.line(
        growth_df, 
        x='year' if period_type == "YoY" else 'period',
        y='growth_rate',
        color='vehicle_type',
        title=f'{period_type} Growth Rate by Vehicle Type',
        color_discrete_map={
            '2W': '#8b5cf6',
            '3W': '#059669', 
            '4W': '#dc2626'
        }
    )
    
    fig.update_layout(
        font_family="DM Sans",
        title_font_family="Space Grotesk",
        title_font_size=18,
        title_font_color="#1f2937",
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(gridcolor='#f1f5f9'),
        yaxis=dict(gridcolor='#f1f5f9', title="Growth Rate (%)"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_market_share_chart(df, vehicle_type):
    """Create market share pie chart"""
    if df.empty:
        return go.Figure()
    
    vehicle_data = df[df['vehicle_type'] == vehicle_type]
    market_share = vehicle_data.groupby('manufacturer')['registrations'].sum().sort_values(ascending=False)
    
    # Take top 8 and group rest as "Others"
    top_manufacturers = market_share.head(8)
    others_sum = market_share.iloc[8:].sum() if len(market_share) > 8 else 0
    
    if others_sum > 0:
        top_manufacturers['Others'] = others_sum
    
    colors = ['#8b5cf6', '#059669', '#dc2626', '#f59e0b', '#3b82f6', '#ef4444', '#10b981', '#6366f1', '#6b7280']
    
    fig = go.Figure(data=[go.Pie(
        labels=top_manufacturers.index,
        values=top_manufacturers.values,
        hole=0.4,
        marker_colors=colors[:len(top_manufacturers)]
    )])
    
    fig.update_layout(
        title=f'{vehicle_type} Market Share',
        font_family="DM Sans",
        title_font_family="Space Grotesk",
        title_font_size=18,
        title_font_color="#1f2937",
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

def create_registration_trends_chart(df):
    """Create overall registration trends chart"""
    if df.empty:
        return go.Figure()
    
    # Monthly trends
    df['date'] = pd.to_datetime(df['date'])
    monthly_data = df.groupby([df['date'].dt.to_period('M'), 'vehicle_type'])['registrations'].sum().reset_index()
    monthly_data['date'] = monthly_data['date'].astype(str)
    
    fig = px.area(
        monthly_data,
        x='date',
        y='registrations',
        color='vehicle_type',
        title='Vehicle Registration Trends Over Time',
        color_discrete_map={
            '2W': '#8b5cf6',
            '3W': '#059669', 
            '4W': '#dc2626'
        }
    )
    
    fig.update_layout(
        font_family="DM Sans",
        title_font_family="Space Grotesk",
        title_font_size=18,
        title_font_color="#1f2937",
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(gridcolor='#f1f5f9', title="Time Period"),
        yaxis=dict(gridcolor='#f1f5f9', title="Registrations"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def main():
    st.markdown('<h1 class="main-header">Vehicle Registration Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">In-Depth Insights for Strategic Investment Decisions</p>', unsafe_allow_html=True)
    
    # Data source information
    st.info("""
    **Data Source**: This dashboard connects to the [Vahan Dashboard](https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml) 
    for real-time vehicle registration data. When the API is unavailable, comprehensive sample data is used for demonstration purposes.
    """)
    
    # Load data
    with st.spinner("Loading vehicle registration data..."):
        df, db_manager = load_data()
    
    if df.empty:
        st.error("No data available. Please run the database initialization script first.")
        st.code("python scripts/initialize_database.py")
        return
    
    # Initialize analytics
    analytics_engine, insights_generator = get_analytics_components(df)
    
    if analytics_engine is None:
        st.error("Failed to initialize analytics engine.")
        return
    
    # Sidebar filters
    st.sidebar.markdown("### Filters & Controls")
    
    # Date range filter - show current date range
    min_date = pd.to_datetime(df['date']).min().date()
    max_date = pd.to_datetime(df['date']).max().date()
    
    # Show current date info
    from datetime import datetime
    today = datetime.now().date()
    st.sidebar.markdown(f"**Data Available:** {min_date} to {max_date}")
    st.sidebar.markdown(f"**Today's Date:** {today}")
    
    if max_date < today:
        st.sidebar.warning(f"⚠️ Data is {today - max_date} days old")
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Select the date range for analysis. Data is updated quarterly."
    )
    
    # Vehicle type filter
    vehicle_types = ['All'] + sorted(df['vehicle_type'].unique().tolist())
    selected_vehicle_type = st.sidebar.selectbox("Vehicle Type", vehicle_types, index=0)
    
    # Manufacturer filter
    manufacturers = ['All'] + sorted(df['manufacturer'].unique().tolist())
    selected_manufacturer = st.sidebar.selectbox("Manufacturer", manufacturers, index=0)
    
    # Apply filters
    filtered_df = df.copy()
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[(
            pd.to_datetime(filtered_df['date']).dt.date >= start_date) & (
            pd.to_datetime(filtered_df['date']).dt.date <= end_date)
        ]
    
    if selected_vehicle_type != 'All':
        filtered_df = filtered_df[filtered_df['vehicle_type'] == selected_vehicle_type]
    
    if selected_manufacturer != 'All':
        filtered_df = filtered_df[filtered_df['manufacturer'] == selected_manufacturer]
    
    # Check if filtered data is empty
    if filtered_df.empty:
        st.warning("No data available for the selected date range and filters. Please adjust your selection or ensure data is fetched up to today.")
        return
    
    # Show filter summary
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Active Filters:**")
    if selected_vehicle_type != 'All':
        st.sidebar.markdown(f"• Vehicle Type: {selected_vehicle_type}")
    if selected_manufacturer != 'All':
        st.sidebar.markdown(f"• Manufacturer: {selected_manufacturer}")
    if len(date_range) == 2:
        start_date, end_date = date_range
        st.sidebar.markdown(f"• Date Range: {start_date} to {end_date}")
    
    st.sidebar.markdown(f"**Filtered Records:** {len(filtered_df):,}")
    
    # Key Metrics Row - Make responsive
    st.markdown('<h2 class="section-header">Key Performance Indicators</h2>', unsafe_allow_html=True)
    
    # Check screen width for layout (Streamlit doesn't have built-in, but we can use a trick or assume wide)
    # For simplicity, add a toggle for testing mobile view
    mobile_view = st.sidebar.checkbox("Simulate Mobile View", False)
    
    if mobile_view:
        # Stack metrics in 2 columns for mobile
        col1, col2 = st.columns(2)
        with col1:
            total_registrations = filtered_df['registrations'].sum()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Total Registrations</div>
                <div class="metric-value">{total_registrations:,}</div>
            </div>
            """, unsafe_allow_html=True)
            
            total_manufacturers = filtered_df['manufacturer'].nunique()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Active Manufacturers</div>
                <div class="metric-value">{total_manufacturers}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            # YoY growth
            current_year = filtered_df['year'].max()
            current_year_data = filtered_df[filtered_df['year'] == current_year]['registrations'].sum()
            previous_year_data = filtered_df[filtered_df['year'] == current_year - 1]['registrations'].sum()
            yoy_growth = ((current_year_data - previous_year_data) / previous_year_data * 100) if previous_year_data > 0 else 0
            growth_class = "positive" if yoy_growth >= 0 else "negative"
            growth_symbol = "↑" if yoy_growth >= 0 else "↓"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">YoY Growth</div>
                <div class="metric-value">{yoy_growth:.1f}%</div>
                <div class="metric-change {growth_class}">{growth_symbol} vs Previous Year</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Market leader
            if not filtered_df.empty:
                market_leader = filtered_df.groupby('manufacturer')['registrations'].sum().idxmax()
                leader_share = (filtered_df[filtered_df['manufacturer'] == market_leader]['registrations'].sum() / 
                              total_registrations * 100)
            else:
                market_leader = "N/A"
                leader_share = 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Market Leader</div>
                <div class="metric-value" style="font-size: 1.2rem;">{market_leader}</div>
                <div class="metric-change">{leader_share:.1f}% Market Share</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_registrations = filtered_df['registrations'].sum()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Total Registrations</div>
                <div class="metric-value">{total_registrations:,}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            total_manufacturers = filtered_df['manufacturer'].nunique()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Active Manufacturers</div>
                <div class="metric-value">{total_manufacturers}</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            # YoY growth
            current_year = filtered_df['year'].max()
            current_year_data = filtered_df[filtered_df['year'] == current_year]['registrations'].sum()
            previous_year_data = filtered_df[filtered_df['year'] == current_year - 1]['registrations'].sum()
            yoy_growth = ((current_year_data - previous_year_data) / previous_year_data * 100) if previous_year_data > 0 else 0
            growth_class = "positive" if yoy_growth >= 0 else "negative"
            growth_symbol = "↑" if yoy_growth >= 0 else "↓"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">YoY Growth</div>
                <div class="metric-value">{yoy_growth:.1f}%</div>
                <div class="metric-change {growth_class}">{growth_symbol} vs Previous Year</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            # Market leader
            if not filtered_df.empty:
                market_leader = filtered_df.groupby('manufacturer')['registrations'].sum().idxmax()
                leader_share = (filtered_df[filtered_df['manufacturer'] == market_leader]['registrations'].sum() / 
                              total_registrations * 100)
            else:
                market_leader = "N/A"
                leader_share = 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Market Leader</div>
                <div class="metric-value" style="font-size: 1.2rem;">{market_leader}</div>
                <div class="metric-change">{leader_share:.1f}% Market Share</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Charts Section
    st.markdown('<h2 class="section-header">Growth Analysis</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        growth_period = st.selectbox("Growth Period", ["YoY", "QoQ"])
        growth_chart = create_growth_chart(filtered_df, growth_period)
        st.plotly_chart(growth_chart, use_container_width=True)
    
    with col2:
        registration_trends = create_registration_trends_chart(filtered_df)
        st.plotly_chart(registration_trends, use_container_width=True)
    
    # Market Share Analysis
    st.markdown('<h2 class="section-header">Market Share Analysis</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    vehicle_types_for_charts = ['2W', '3W', '4W']
    for i, vtype in enumerate(vehicle_types_for_charts):
        with [col1, col2, col3][i]:
            market_share_chart = create_market_share_chart(filtered_df, vtype)
            st.plotly_chart(market_share_chart, use_container_width=True)
    
    # Investment Insights
    st.markdown('<h2 class="section-header">Investment Insights</h2>', unsafe_allow_html=True)
    
    # Generate executive summary
    exec_summary = insights_generator.generate_executive_summary(filtered_df)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">Market Overview</div>
            <div class="insight-text">
                <strong>Investment Outlook:</strong> {exec_summary['investment_outlook']}<br><br>
                <strong>Key Highlights:</strong><br>
                {'<br>'.join(['• ' + highlight for highlight in exec_summary['key_highlights'][:3]])}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Investment scorecard
        scorecard = analytics_engine.generate_investment_scorecard(filtered_df)
        
        if scorecard and len(scorecard) > 0:
            best_segment = max(scorecard.items(), key=lambda x: x[1]['overall_score'])
            
            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-title">Investment Recommendation</div>
                <div class="insight-text">
                    <strong>Top Opportunity:</strong> {best_segment[0]} Segment<br>
                    <strong>Score:</strong> {best_segment[1]['overall_score']}/100<br>
                    <strong>Recommendation:</strong> {best_segment[1]['recommendation']}<br><br>
                    <strong>Key Metrics:</strong><br>
                    • Growth: {best_segment[1]['key_metrics']['avg_yoy_growth']:.1f}% YoY<br>
                    • Leader: {best_segment[1]['key_metrics']['market_leader']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-title">Investment Recommendation</div>
                <div class="insight-text">
                    <strong>Status:</strong> Insufficient data for analysis<br>
                    <strong>Recommendation:</strong> Please adjust filters or ensure data is available for the selected period.
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Investment Themes
    themes = insights_generator.identify_investment_themes(filtered_df)
    
    if themes:
        st.markdown('<h2 class="section-header">Investment Themes</h2>', unsafe_allow_html=True)
        
        for i, theme in enumerate(themes[:3]):  # Show top 3 themes
            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-title">{theme.theme_name}</div>
                <div class="insight-text">
                    <strong>Description:</strong> {theme.description}<br>
                    <strong>Investment Thesis:</strong> {theme.investment_thesis}<br>
                    <strong>Potential Returns:</strong> {theme.potential_returns}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #6b7280; font-family: DM Sans;">Vehicle Registration Analytics Dashboard | Data-Driven Investment Intelligence</p>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
