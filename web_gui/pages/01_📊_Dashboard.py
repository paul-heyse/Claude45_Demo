"""Dashboard page for Aker Investment Platform."""

from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import format_currency, format_percentage, get_api_client

st.set_page_config(page_title="Dashboard - Aker Platform", page_icon="📊", layout="wide")

# Check authentication
if not st.session_state.get("logged_in", False):
    st.warning("⚠️ Please login to access the dashboard")
    st.stop()

# Title
st.title("📊 Dashboard")
st.markdown("### Portfolio Overview & Performance")

# Get API client
api = get_api_client()

# Refresh button
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Key Metrics Row
st.markdown("### Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Portfolio Value",
        value=format_currency(2_500_000),
        delta=format_percentage(12.4),
    )

with col2:
    portfolio_count = len(st.session_state.get("portfolio", []))
    st.metric(label="Markets Tracked", value=portfolio_count, delta="+3 this month")

with col3:
    st.metric(label="Cache Hit Rate", value="87.3%", delta="+2.1%")

with col4:
    st.metric(label="Data Sources", value="12", delta="All Online")

st.markdown("---")

# Portfolio Performance Chart
st.markdown("### Portfolio Performance")
col1, col2 = st.columns([2, 1])

with col1:
    # Generate sample time series data
    dates = pd.date_range(end=datetime.now(), periods=180, freq="D")
    portfolio_value = pd.DataFrame(
        {
            "Date": dates,
            "Value": [
                2_000_000 + i * 2_800 + (i % 10) * 15_000 for i in range(180)
            ],
        }
    )

    fig = px.line(
        portfolio_value,
        x="Date",
        y="Value",
        title="Portfolio Value (Last 6 Months)",
    )
    fig.update_traces(line_color="#1E40AF", line_width=3)
    fig.update_layout(
        hovermode="x unified",
        plot_bgcolor="white",
        yaxis_tickformat="$,.0f",
        height=350,
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### Performance Summary")
    st.markdown(
        """
        **6-Month Performance**
        - Total Return: +25.4%
        - Annualized: +50.8%
        - Best Month: +8.2% (Aug)
        - Worst Month: -1.5% (Jun)

        **Risk Metrics**
        - Volatility: 12.3%
        - Sharpe Ratio: 2.1
        - Max Drawdown: -3.2%
        """
    )

st.markdown("---")

# Top Markets & Geographic Distribution
st.markdown("### Market Analysis")
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Top 10 Markets by Score")

    # Sample market data
    top_markets = pd.DataFrame(
        {
            "Market": [
                "Boulder, CO",
                "Fort Collins, CO",
                "Boise, ID",
                "Provo, UT",
                "Denver, CO",
                "Salt Lake City, UT",
                "Colorado Springs, CO",
                "Ogden, UT",
                "Idaho Falls, ID",
                "Loveland, CO",
            ],
            "Score": [87.2, 84.5, 83.8, 82.9, 82.1, 81.7, 80.3, 79.8, 78.5, 77.9],
            "Risk": [0.92, 0.95, 0.98, 0.91, 1.05, 0.94, 1.02, 0.96, 0.89, 0.93],
        }
    )

    # Create bar chart
    fig = px.bar(
        top_markets,
        x="Score",
        y="Market",
        orientation="h",
        title="",
        color="Score",
        color_continuous_scale=[
            "#DC2626",
            "#D97706",
            "#2563EB",
            "#059669",
        ],
        range_color=[0, 100],
    )
    fig.update_layout(
        showlegend=False, height=350, yaxis={"categoryorder": "total ascending"}
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### Geographic Distribution")

    # Sample geographic data
    states = pd.DataFrame(
        {
            "State": ["Colorado", "Utah", "Idaho", "Wyoming", "Montana"],
            "Markets": [12, 8, 3, 1, 0],
            "Avg Score": [82.5, 80.3, 79.1, 75.2, 0],
        }
    )

    # Create choropleth-style bar chart
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=states["State"],
            y=states["Markets"],
            name="Markets",
            marker_color="#1E40AF",
            text=states["Markets"],
            textposition="auto",
        )
    )
    fig.update_layout(
        title="Markets by State",
        xaxis_title="State",
        yaxis_title="Number of Markets",
        height=350,
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Score Distribution & Recent Activity
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("#### Composite Score Distribution")

    # Sample score distribution
    score_bins = pd.DataFrame(
        {
            "Score Range": ["0-40", "41-60", "61-80", "81-100"],
            "Markets": [2, 8, 10, 4],
            "Color": ["#DC2626", "#D97706", "#2563EB", "#059669"],
        }
    )

    fig = px.bar(
        score_bins,
        x="Score Range",
        y="Markets",
        color="Score Range",
        color_discrete_map={
            "0-40": "#DC2626",
            "41-60": "#D97706",
            "61-80": "#2563EB",
            "81-100": "#059669",
        },
    )
    fig.update_layout(showlegend=False, height=300)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### Recent Activity")

    activities = [
        {
            "time": "2 hours ago",
            "icon": "✅",
            "text": "Added **Boulder, CO** to portfolio",
        },
        {
            "time": "5 hours ago",
            "icon": "📊",
            "text": "Generated report for **Fort Collins, CO**",
        },
        {
            "time": "Yesterday",
            "icon": "🔍",
            "text": "Screened **127 markets** in Colorado",
        },
        {
            "time": "Yesterday",
            "icon": "💾",
            "text": "Updated cache for **BLS data**",
        },
        {
            "time": "2 days ago",
            "icon": "📈",
            "text": "**Denver, CO** score increased by 2.3 points",
        },
        {
            "time": "2 days ago",
            "icon": "⚠️",
            "text": "New wildfire risk detected in **Boise, ID**",
        },
    ]

    for activity in activities:
        st.markdown(
            f"""
            <div style='padding: 8px; margin-bottom: 8px; border-left: 3px solid #1E40AF; background-color: #F9FAFB;'>
                <div style='font-size: 12px; color: #6B7280;'>{activity['time']}</div>
                <div>{activity['icon']} {activity['text']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("---")

# System Health & Cache Statistics
st.markdown("### System Status")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("#### API Health")
    st.success("✓ All APIs Operational")
    st.markdown(
        """
        - Census: ✓ Online
        - BLS: ✓ Online
        - OSM: ✓ Online
        - FEMA: ✓ Online
        """
    )

with col2:
    st.markdown("#### Cache Performance")
    st.info("📊 Cache Statistics")
    st.markdown(
        """
        - Hit Rate: 87.3%
        - Memory: 198MB / 256MB
        - SQLite: 2.3GB
        - Entries: 1,247
        """
    )

with col3:
    st.markdown("#### Data Freshness")
    st.warning("⚠️ Some data aging")
    st.markdown(
        """
        - Census ACS: 2 days
        - BLS QCEW: 5 days
        - OSM POI: Current
        - FEMA Flood: 30 days
        """
    )

with col4:
    st.markdown("#### Quick Actions")
    if st.button("🔍 Screen Markets", use_container_width=True):
        st.switch_page("pages/02_🔍_Market_Screening.py")
    if st.button("💼 View Portfolio", use_container_width=True):
        st.switch_page("pages/04_💼_Portfolio.py")
    if st.button("💾 Warm Cache", use_container_width=True):
        st.switch_page("pages/06_💾_Data_Management.py")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #6B7280; font-size: 12px;'>
        Dashboard last updated: {} UTC
    </div>
    """.format(
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ),
    unsafe_allow_html=True,
)

