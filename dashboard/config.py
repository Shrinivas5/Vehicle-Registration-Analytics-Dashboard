"""
Configuration settings for the Vahan Dashboard
"""

# Dashboard settings
DASHBOARD_CONFIG = {
    'title': 'Vehicle Registration Analytics Dashboard',
    'subtitle': 'In-Depth Insights for Strategic Investment Decisions',
    'page_icon': '🚗',
    'layout': 'wide'
}

# Color scheme (following design brief)
COLORS = {
    'primary': '#1f2937',      # Deep gray
    'accent': '#8b5cf6',       # Purple
    'success': '#059669',      # Green
    'warning': '#f59e0b',      # Amber
    'danger': '#dc2626',       # Red
    'light_gray': '#f1f5f9',   # Light gray
    'medium_gray': '#6b7280',  # Medium gray
    'white': '#ffffff'         # White
}

# Chart color mappings
VEHICLE_TYPE_COLORS = {
    '2W': COLORS['accent'],    # Purple for 2-wheelers
    '3W': COLORS['success'],   # Green for 3-wheelers
    '4W': COLORS['danger']     # Red for 4-wheelers
}

# Typography settings
FONTS = {
    'heading': 'Space Grotesk',
    'body': 'DM Sans'
}

# Data refresh settings
CACHE_TTL = 300  # 5 minutes

# Analytics settings
ANALYTICS_CONFIG = {
    'forecast_periods': 4,
    'top_manufacturers_count': 10,
    'growth_threshold_high': 15,  # % growth considered high
    'growth_threshold_low': -5,   # % growth considered concerning
    'market_concentration_threshold': 2500  # HHI threshold for high concentration
}

# Dashboard sections configuration
SECTIONS = {
    'kpis': {
        'title': 'Key Performance Indicators',
        'enabled': True
    },
    'growth_analysis': {
        'title': 'Growth Analysis',
        'enabled': True
    },
    'market_share': {
        'title': 'Market Share Analysis',
        'enabled': True
    },
    'investment_insights': {
        'title': 'Investment Insights',
        'enabled': True
    },
    'investment_themes': {
        'title': 'Investment Themes',
        'enabled': True
    }
}
