"""Market Details page for Aker Investment Platform."""

from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import (
    format_currency,
    format_percentage,
    format_score,
    get_api_client,
    get_score_color_hex,
    get_score_label,
)

st.set_page_config(
    page_title="Market Details - Aker Platform", page_icon="📍", layout="wide"
)

# Check authentication
if not st.session_state.get("logged_in", False):
    st.warning("⚠️ Please login to access market details")
    st.stop()

# Market selection
selected_market = st.session_state.get("selected_market", "Boulder, CO")

# Title with market selector
col1, col2 = st.columns([3, 1])
with col1:
    st.title(f"📍 {selected_market}")
    st.markdown("### Comprehensive Market Analysis")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔙 Back to Screening", use_container_width=True):
        st.switch_page("pages/02_🔍_Market_Screening.py")

# Sample market data (in production, fetch from API)
market_data = {
    "market": selected_market,
    "state": "CO",
    "cbsa": "14500",
    "composite_score": 87.2,
    "supply_score": 95.1,
    "jobs_score": 82.3,
    "urban_score": 78.9,
    "outdoor_score": 91.5,
    "risk_multiplier": 0.92,
    "population": 330_758,
    "median_income": 78_642,
    "employment": 185_420,
}

# Composite Score Display
st.markdown("### Composite Score")
col1, col2, col3 = st.columns([1, 2, 2])

with col1:
    score_color = get_score_color_hex(market_data["composite_score"])
    score_label = get_score_label(market_data["composite_score"])

    st.markdown(
        f"""
        <div style='text-align: center; padding: 30px; background: linear-gradient(135deg, #1E40AF 0%, {score_color} 100%); border-radius: 12px; color: white;'>
            <div style='font-size: 64px; font-weight: 700; line-height: 1;'>{market_data['composite_score']:.1f}</div>
            <div style='font-size: 24px; margin-top: 8px;'>{score_label}</div>
            <div style='font-size: 14px; margin-top: 8px; opacity: 0.9;'>Composite Score</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Add to portfolio button
    if st.button("➕ Add to Portfolio", use_container_width=True, type="primary"):
        if "portfolio" not in st.session_state:
            st.session_state.portfolio = []
        st.session_state.portfolio.append(market_data)
        st.success(f"Added {selected_market} to portfolio!")

with col2:
    st.markdown("#### Score Breakdown")

    # Radar chart
    categories = ["Supply\nConstraint", "Innovation\nJobs", "Urban\nConvenience", "Outdoor\nAccess"]
    values = [
        market_data["supply_score"],
        market_data["jobs_score"],
        market_data["urban_score"],
        market_data["outdoor_score"],
    ]

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values,
            theta=categories,
            fill="toself",
            name=selected_market,
            fillcolor="rgba(30, 64, 175, 0.3)",
            line=dict(color="#1E40AF", width=3),
        )
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        height=300,
    )
    st.plotly_chart(fig, use_container_width=True)

with col3:
    st.markdown("#### Risk Assessment")

    # Gauge chart for risk multiplier
    risk_value = market_data["risk_multiplier"]
    risk_color = "#059669" if risk_value < 1.0 else "#DC2626" if risk_value > 1.1 else "#D97706"

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=risk_value,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Risk Multiplier"},
            delta={"reference": 1.0},
            gauge={
                "axis": {"range": [0.7, 1.3]},
                "bar": {"color": risk_color},
                "steps": [
                    {"range": [0.7, 0.9], "color": "#D1FAE5"},
                    {"range": [0.9, 1.1], "color": "#FEF3C7"},
                    {"range": [1.1, 1.3], "color": "#FEE2E2"},
                ],
                "threshold": {
                    "line": {"color": "black", "width": 2},
                    "thickness": 0.75,
                    "value": 1.0,
                },
            },
        )
    )
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Detailed Scores
st.markdown("### Component Scores")
col1, col2, col3, col4 = st.columns(4)

with col1:
    score_color = get_score_color_hex(market_data["supply_score"])
    st.markdown(
        f"""
        <div style='text-align: center; padding: 20px; border: 2px solid {score_color}; border-radius: 8px;'>
            <div style='font-size: 36px; font-weight: 600; color: {score_color};'>{market_data['supply_score']:.1f}</div>
            <div style='font-size: 14px; color: #6B7280; margin-top: 8px;'>Supply Constraint</div>
            <div style='font-size: 11px; color: {score_color}; margin-top: 4px;'>{get_score_label(market_data['supply_score'])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    score_color = get_score_color_hex(market_data["jobs_score"])
    st.markdown(
        f"""
        <div style='text-align: center; padding: 20px; border: 2px solid {score_color}; border-radius: 8px;'>
            <div style='font-size: 36px; font-weight: 600; color: {score_color};'>{market_data['jobs_score']:.1f}</div>
            <div style='font-size: 14px; color: #6B7280; margin-top: 8px;'>Innovation Jobs</div>
            <div style='font-size: 11px; color: {score_color}; margin-top: 4px;'>{get_score_label(market_data['jobs_score'])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    score_color = get_score_color_hex(market_data["urban_score"])
    st.markdown(
        f"""
        <div style='text-align: center; padding: 20px; border: 2px solid {score_color}; border-radius: 8px;'>
            <div style='font-size: 36px; font-weight: 600; color: {score_color};'>{market_data['urban_score']:.1f}</div>
            <div style='font-size: 14px; color: #6B7280; margin-top: 8px;'>Urban Convenience</div>
            <div style='font-size: 11px; color: {score_color}; margin-top: 4px;'>{get_score_label(market_data['urban_score'])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    score_color = get_score_color_hex(market_data["outdoor_score"])
    st.markdown(
        f"""
        <div style='text-align: center; padding: 20px; border: 2px solid {score_color}; border-radius: 8px;'>
            <div style='font-size: 36px; font-weight: 600; color: {score_color};'>{market_data['outdoor_score']:.1f}</div>
            <div style='font-size: 14px; color: #6B7280; margin-top: 8px;'>Outdoor Access</div>
            <div style='font-size: 11px; color: {score_color}; margin-top: 4px;'>{get_score_label(market_data['outdoor_score'])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# Historical Trends
st.markdown("### Historical Trends")

tabs = st.tabs(["📈 Employment", "🏗️ Building Permits", "👥 Population", "💰 Income"])

with tabs[0]:
    st.markdown("#### Employment Growth (Last 5 Years)")
    years = list(range(2019, 2024))
    employment = [175_000, 178_500, 172_000, 180_200, 185_420]

    df = pd.DataFrame({"Year": years, "Employment": employment})
    fig = px.line(df, x="Year", y="Employment", markers=True)
    fig.update_traces(line_color="#1E40AF", line_width=3, marker_size=8)
    fig.update_layout(hovermode="x unified", height=350)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("5-Year Growth", "+6.0%", "+10,420 jobs")
    with col2:
        st.metric("CAGR", "+1.2%", "")
    with col3:
        st.metric("2023 Change", "+2.9%", "+5,220 jobs")

with tabs[1]:
    st.markdown("#### Building Permits (Last 5 Years)")
    permits = [2_850, 3_120, 2_680, 3_420, 3_890]

    df = pd.DataFrame({"Year": years, "Permits": permits})
    fig = px.bar(df, x="Year", y="Permits", color="Permits", color_continuous_scale="Blues")
    fig.update_layout(showlegend=False, height=350)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total (5 Years)", "15,960", "permits")
    with col2:
        st.metric("2023 Total", "3,890", "+13.7%")
    with col3:
        st.metric("Avg Annual", "3,192", "permits")

with tabs[2]:
    st.markdown("#### Population Growth (Last 10 Years)")
    pop_years = list(range(2014, 2024))
    population = [
        297_234,
        302_567,
        308_125,
        312_897,
        318_456,
        323_128,
        326_543,
        328_967,
        329_785,
        330_758,
    ]

    df = pd.DataFrame({"Year": pop_years, "Population": population})
    fig = px.area(df, x="Year", y="Population")
    fig.update_traces(fillcolor="rgba(30, 64, 175, 0.3)", line_color="#1E40AF", line_width=3)
    fig.update_layout(hovermode="x unified", height=350)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("10-Year Growth", "+11.3%", "+33,524")
    with col2:
        st.metric("CAGR", "+1.1%", "")
    with col3:
        st.metric("2023 Change", "+0.3%", "+973")

with tabs[3]:
    st.markdown("#### Median Household Income (Last 5 Years)")
    income = [72_450, 74_230, 75_890, 77_120, 78_642]

    df = pd.DataFrame({"Year": years, "Income": income})
    fig = px.line(df, x="Year", y="Income", markers=True)
    fig.update_traces(line_color="#059669", line_width=3, marker_size=8)
    fig.update_layout(hovermode="x unified", yaxis_tickformat="$,.0f", height=350)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("5-Year Growth", "+8.5%", "+$6,192")
    with col2:
        st.metric("Current Median", "$78,642", "+2.0%")
    with col3:
        st.metric("Above State Avg", "+12.3%", "")

st.markdown("---")

# Market Demographics
st.markdown("### Market Demographics")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### Population")
    st.metric("Total Population", f"{market_data['population']:,}", "+0.3% YoY")
    st.markdown(
        """
        - Age 25-34: 18.2%
        - Age 35-44: 16.5%
        - Age 45-54: 14.8%
        - Bachelor's+: 71.2%
        """
    )

with col2:
    st.markdown("#### Economics")
    st.metric("Median Income", f"${market_data['median_income']:,}", "+2.0% YoY")
    st.markdown(
        """
        - Median Home: $685,000
        - Rent (1BR): $1,850/mo
        - Unemployment: 2.8%
        - Labor Force: 198,750
        """
    )

with col3:
    st.markdown("#### Industry Mix")
    industries = pd.DataFrame(
        {
            "Industry": ["Tech", "Education", "Healthcare", "Retail", "Other"],
            "Share": [28.5, 18.2, 12.8, 9.5, 31.0],
        }
    )
    fig = px.pie(industries, values="Share", names="Industry", hole=0.4)
    fig.update_layout(showlegend=True, height=200, margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Data Sources
st.markdown("### Data Sources")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        """
        **Census Bureau**
        - ACS 5-Year: 2022
        - Updated: 2 days ago
        - Status: ✓ Current
        """
    )

with col2:
    st.markdown(
        """
        **Bureau of Labor Statistics**
        - QCEW: Q4 2023
        - Updated: 5 days ago
        - Status: ✓ Current
        """
    )

with col3:
    st.markdown(
        """
        **OpenStreetMap**
        - POI Data: Current
        - Updated: Real-time
        - Status: ✓ Current
        """
    )

with col4:
    st.markdown(
        """
        **FEMA**
        - Flood Maps: 2023
        - Updated: 30 days ago
        - Status: ⚠️ Aging
        """
    )

# Actions
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📊 Generate Report", use_container_width=True, type="primary"):
        st.session_state.report_market = selected_market
        st.switch_page("pages/05_📊_Reports.py")

with col2:
    if st.button("📈 Compare Markets", use_container_width=True):
        st.switch_page("pages/04_💼_Portfolio.py")

with col3:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.success("Data refreshed successfully!")

with col4:
    if st.button("📤 Export Analysis", use_container_width=True):
        st.info("Export functionality coming soon...")

