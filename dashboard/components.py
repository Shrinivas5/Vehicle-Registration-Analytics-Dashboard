"""
Reusable dashboard components
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from dashboard.config import COLORS, VEHICLE_TYPE_COLORS, FONTS

def render_metric_card(title: str, value: str, change: str = None, change_type: str = "neutral"):
    """Render a professional metric card"""
    change_class = {
        "positive": "positive",
        "negative": "negative",
        "neutral": ""
    }.get(change_type, "")
    
    change_symbol = {
        "positive": "↑",
        "negative": "↓",
        "neutral": ""
    }.get(change_type, "")
    
    change_html = f'<div class="metric-change {change_class}">{change_symbol} {change}</div>' if change else ""
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        {change_html}
    </div>
    """, unsafe_allow_html=True)

// Add hover effect in CSS (already added in main.py)

def render_insight_card(title: str, content: str, card_type: str = "default"):
    st.markdown(f"""
    <div class="insight-card" style="transition: all 0.3s ease;">
        <div class="insight-title">{title}</div>
        <div class="insight-text">{content}</div>
    </div>
    """, unsafe_allow_html=True)

def create_professional_chart_layout(fig, title: str):
    """Apply professional styling to charts"""
    fig.update_layout(
        font_family=FONTS['body'],
        title_font_family=FONTS['heading'],
        title_font_size=18,
        title_font_color=COLORS['primary'],
        plot_bgcolor=COLORS['white'],
        paper_bgcolor=COLORS['white'],
        xaxis=dict(gridcolor=COLORS['light_gray']),
        yaxis=dict(gridcolor=COLORS['light_gray']),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        title=title
    )
    return fig

def render_loading_state(message: str = "Loading data..."):
    """Render a professional loading state"""
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem;">
        <div style="font-family: {FONTS['body']}; color: {COLORS['medium_gray']}; font-size: 1.1rem;">
            {message}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_section_header(title: str):
    """Render a professional section header"""
    st.markdown(f'<h2 class="section-header">{title}</h2>', unsafe_allow_html=True)

def render_error_state(message: str):
    """Render a professional error state"""
    st.markdown(f"""
    <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 1rem; margin: 1rem 0;">
        <div style="color: #dc2626; font-family: {FONTS['body']}; font-weight: 500;">
            Error: {message}
        </div>
    </div>
    """, unsafe_allow_html=True)
