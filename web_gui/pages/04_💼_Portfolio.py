"""Portfolio Management page for Aker Investment Platform."""

from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import format_currency, format_percentage, get_score_color_hex, get_score_label

st.set_page_config(
    page_title="Portfolio - Aker Platform", page_icon="💼", layout="wide"
)

# Check authentication
if not st.session_state.get("logged_in", False):
    st.warning("⚠️ Please login to access portfolio management")
    st.stop()

# Title
st.title("💼 Portfolio Management")
st.markdown("### Track & Manage Investment Prospects")

# Initialize portfolio if not exists
if "portfolio" not in st.session_state:
    st.session_state.portfolio = []

# Portfolio summary metrics
st.markdown("### Portfolio Overview")
col1, col2, col3, col4 = st.columns(4)

# Sample portfolio data (in production, fetch from backend)
sample_portfolio = [
    {
        "Market": "Boulder, CO",
        "State": "CO",
        "Score": 87.2,
        "Risk": 0.92,
        "Status": "Prospect",
        "Added": datetime.now() - timedelta(days=5),
        "Notes": "High innovation employment, excellent outdoor access",
    },
    {
        "Market": "Fort Collins, CO",
        "State": "CO",
        "Score": 84.5,
        "Risk": 0.95,
        "Status": "Committed",
        "Added": datetime.now() - timedelta(days=12),
        "Notes": "Strong university presence, growing tech sector",
    },
    {
        "Market": "Boise, ID",
        "State": "ID",
        "Score": 83.8,
        "Risk": 0.98,
        "Status": "Prospect",
        "Added": datetime.now() - timedelta(days=8),
        "Notes": "Rapid population growth, good supply constraint",
    },
    {
        "Market": "Provo, UT",
        "State": "UT",
        "Score": 82.9,
        "Risk": 0.91,
        "Status": "Active",
        "Added": datetime.now() - timedelta(days=20),
        "Notes": "Silicon Slopes tech hub, young demographics",
    },
]

# Use sample data if portfolio is empty
if not st.session_state.portfolio:
    st.session_state.portfolio = sample_portfolio

portfolio_df = pd.DataFrame(st.session_state.portfolio)

with col1:
    st.metric("Total Markets", len(portfolio_df), "+3 this month")

with col2:
    avg_score = portfolio_df["Score"].mean() if not portfolio_df.empty else 0
    st.metric("Avg Composite Score", f"{avg_score:.1f}", "+1.2")

with col3:
    avg_risk = portfolio_df["Risk"].mean() if not portfolio_df.empty else 0
    risk_delta = "+2.3%" if avg_risk < 1.0 else "-2.3%"
    st.metric("Avg Risk Multiplier", f"{avg_risk:.2f}x", risk_delta)

with col4:
    est_value = len(portfolio_df) * 450_000  # Estimated $450k per market
    st.metric("Est. Portfolio Value", format_currency(est_value), "+12.5%")

st.markdown("---")

# Add market button
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("➕ Add Market", use_container_width=True):
        st.switch_page("pages/02_🔍_Market_Screening.py")

# Portfolio table
st.markdown("### Portfolio Markets")

if portfolio_df.empty:
    st.info("📭 Your portfolio is empty. Add markets from the screening page.")
else:
    # Selection for bulk actions
    selected_indices = []

    for idx, row in portfolio_df.iterrows():
        with st.container():
            col1, col2, col3, col4, col5, col6, col7 = st.columns([0.5, 2, 1, 1, 1, 2, 1])

            with col1:
                if st.checkbox("", key=f"select_{idx}", label_visibility="collapsed"):
                    selected_indices.append(idx)

            with col2:
                st.markdown(
                    f"**{row['Market']}**<br><span style='color: #6B7280; font-size: 12px;'>{row['State']}</span>",
                    unsafe_allow_html=True,
                )

            with col3:
                added_date = row["Added"]
                if isinstance(added_date, str):
                    date_str = added_date
                else:
                    date_str = added_date.strftime("%Y-%m-%d")
                st.markdown(
                    f"<span style='font-size: 12px; color: #6B7280;'>{date_str}</span>",
                    unsafe_allow_html=True,
                )

            with col4:
                score_color = get_score_color_hex(row["Score"])
                st.markdown(
                    f"<div style='text-align: center;'>"
                    f"<span style='color: {score_color}; font-size: 20px; font-weight: 600;'>{row['Score']:.1f}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

            with col5:
                risk_color = "#059669" if row["Risk"] < 1.0 else "#DC2626" if row["Risk"] > 1.1 else "#D97706"
                st.markdown(
                    f"<div style='text-align: center; color: {risk_color}; font-weight: 600;'>{row['Risk']:.2f}x</div>",
                    unsafe_allow_html=True,
                )

            with col6:
                status = row.get("Status", "Prospect")
                status_colors = {
                    "Prospect": "#2563EB",
                    "Committed": "#D97706",
                    "Active": "#059669",
                }
                status_color = status_colors.get(status, "#6B7280")
                st.markdown(
                    f"<span style='background: {status_color}20; color: {status_color}; "
                    f"padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;'>{status}</span>",
                    unsafe_allow_html=True,
                )

            with col7:
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    if st.button("📍", key=f"view_{idx}", help="View Details"):
                        st.session_state.selected_market = row["Market"]
                        st.switch_page("pages/03_📍_Market_Details.py")
                with col_b:
                    if st.button("✏️", key=f"edit_{idx}", help="Edit Notes"):
                        st.session_state.editing_market = idx
                with col_c:
                    if st.button("🗑️", key=f"del_{idx}", help="Remove"):
                        st.session_state.portfolio.pop(idx)
                        st.rerun()

            # Show notes if exists
            if row.get("Notes"):
                st.markdown(
                    f"<span style='font-size: 12px; color: #6B7280;'>📝 {row['Notes']}</span>",
                    unsafe_allow_html=True,
                )

            st.markdown("<hr style='margin: 8px 0;'>", unsafe_allow_html=True)

    # Bulk actions
    if selected_indices:
        st.markdown(f"**{len(selected_indices)} markets selected**")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("📊 Compare Selected", use_container_width=True, type="primary"):
                st.session_state.compare_markets = [
                    portfolio_df.iloc[i]["Market"] for i in selected_indices
                ]
                st.info("Comparison view coming soon...")

        with col2:
            if st.button("📄 Export Selected", use_container_width=True):
                selected_df = portfolio_df.iloc[selected_indices]
                csv = selected_df.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv,
                    "portfolio_selection.csv",
                    "text/csv",
                    use_container_width=True,
                )

        with col3:
            if st.button("📊 Generate Report", use_container_width=True):
                st.session_state.report_markets = [
                    portfolio_df.iloc[i]["Market"] for i in selected_indices
                ]
                st.switch_page("pages/05_📊_Reports.py")

        with col4:
            if st.button("🗑️ Remove Selected", use_container_width=True):
                for idx in sorted(selected_indices, reverse=True):
                    st.session_state.portfolio.pop(idx)
                st.rerun()

st.markdown("---")

# Portfolio analytics
st.markdown("### Portfolio Analytics")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Score Distribution")

    if not portfolio_df.empty:
        fig = px.histogram(
            portfolio_df,
            x="Score",
            nbins=10,
            title="",
            color_discrete_sequence=["#1E40AF"],
        )
        fig.update_layout(
            xaxis_title="Composite Score",
            yaxis_title="Number of Markets",
            height=300,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data to display")

with col2:
    st.markdown("#### Status Breakdown")

    if not portfolio_df.empty:
        status_counts = portfolio_df["Status"].value_counts()
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            hole=0.4,
            color_discrete_map={
                "Prospect": "#2563EB",
                "Committed": "#D97706",
                "Active": "#059669",
            },
        )
        fig.update_layout(height=300, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data to display")

st.markdown("---")

# Portfolio performance over time
st.markdown("### Portfolio Performance")

if not portfolio_df.empty:
    # Generate sample time series
    dates = pd.date_range(end=datetime.now(), periods=90, freq="D")
    portfolio_scores = pd.DataFrame(
        {
            "Date": dates,
            "Avg Score": [80 + (i % 30) * 0.1 for i in range(90)],
            "Avg Risk": [0.95 + (i % 20) * 0.001 for i in range(90)],
        }
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=portfolio_scores["Date"],
            y=portfolio_scores["Avg Score"],
            mode="lines",
            name="Avg Composite Score",
            line=dict(color="#1E40AF", width=3),
        )
    )
    fig.update_layout(
        title="Average Composite Score (Last 90 Days)",
        xaxis_title="Date",
        yaxis_title="Score",
        hovermode="x unified",
        height=350,
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("90-Day Change", "+2.3 points", "+2.9%")
    with col2:
        st.metric("Best Performer", "Boulder, CO", "+5.1 pts")
    with col3:
        st.metric("Portfolio Trend", "📈 Improving", "")
else:
    st.info("Add markets to your portfolio to see performance tracking")

st.markdown("---")

# Alerts and notifications
st.markdown("### Portfolio Alerts")

alerts = [
    {
        "type": "success",
        "icon": "✅",
        "market": "Boulder, CO",
        "message": "Score increased by 2.1 points (now 87.2)",
        "time": "2 hours ago",
    },
    {
        "type": "warning",
        "icon": "⚠️",
        "market": "Boise, ID",
        "message": "New wildfire risk detected in area",
        "time": "1 day ago",
    },
    {
        "type": "info",
        "icon": "📊",
        "market": "Fort Collins, CO",
        "message": "New employment data available",
        "time": "2 days ago",
    },
]

for alert in alerts:
    alert_colors = {"success": "#059669", "warning": "#D97706", "info": "#2563EB"}
    color = alert_colors.get(alert["type"], "#6B7280")

    st.markdown(
        f"""
        <div style='padding: 12px; margin-bottom: 8px; border-left: 4px solid {color}; background-color: {color}10; border-radius: 4px;'>
            <div style='display: flex; justify-content: space-between;'>
                <div>
                    <span style='font-size: 18px;'>{alert['icon']}</span>
                    <strong>{alert['market']}</strong>: {alert['message']}
                </div>
                <div style='color: #6B7280; font-size: 12px;'>{alert['time']}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

