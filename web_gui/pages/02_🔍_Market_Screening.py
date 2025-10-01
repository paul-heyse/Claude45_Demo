"""Market Screening page for Aker Investment Platform."""

import pandas as pd
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
    page_title="Market Screening - Aker Platform", page_icon="🔍", layout="wide"
)

# Check authentication
if not st.session_state.get("logged_in", False):
    st.warning("⚠️ Please login to access market screening")
    st.stop()

# Title
st.title("🔍 Market Screening")
st.markdown("### Find Investment Opportunities")

# Search and Filter Section
st.markdown("#### Search & Filters")

# Search bar
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    search_term = st.text_input(
        "Search markets",
        placeholder="Enter city, county, or state...",
        label_visibility="collapsed",
    )
with col2:
    if st.button("🔍 Screen", use_container_width=True, type="primary"):
        st.session_state.filters_applied = True
with col3:
    if st.button("🔄 Reset", use_container_width=True):
        st.session_state.filters = {}
        st.session_state.filters_applied = False
        st.rerun()

# Expandable filter panel
with st.expander("⚙️ Advanced Filters", expanded=True):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Score Filters**")
        supply_min = st.slider(
            "Supply Constraint (min)",
            0,
            100,
            st.session_state.get("filters", {}).get("supply_min", 0),
            help="Minimum supply constraint score (0-100)",
        )

        jobs_min = st.slider(
            "Innovation Jobs (min)",
            0,
            100,
            st.session_state.get("filters", {}).get("jobs_min", 0),
            help="Minimum innovation employment score (0-100)",
        )

        urban_min = st.slider(
            "Urban Convenience (min)",
            0,
            100,
            st.session_state.get("filters", {}).get("urban_min", 0),
            help="Minimum urban convenience score (0-100)",
        )

    with col2:
        st.markdown("**Risk & Location**")
        risk_max = st.slider(
            "Risk Multiplier (max)",
            0.7,
            1.3,
            st.session_state.get("filters", {}).get("risk_max", 1.3),
            0.05,
            help="Maximum acceptable risk multiplier",
        )

        outdoor_min = st.slider(
            "Outdoor Access (min)",
            0,
            100,
            st.session_state.get("filters", {}).get("outdoor_min", 0),
            help="Minimum outdoor access score (0-100)",
        )

        composite_min = st.slider(
            "Composite Score (min)",
            0,
            100,
            st.session_state.get("filters", {}).get("composite_min", 0),
            help="Minimum composite score (0-100)",
        )

    # Save filters to session state
    st.session_state.filters = {
        "supply_min": supply_min,
        "jobs_min": jobs_min,
        "urban_min": urban_min,
        "outdoor_min": outdoor_min,
        "risk_max": risk_max,
        "composite_min": composite_min,
    }

st.markdown("---")

# Batch screening
st.markdown("#### Batch Screening")
col1, col2 = st.columns([3, 1])
with col1:
    uploaded_file = st.file_uploader(
        "Upload CSV with market list (City, State columns required)",
        type=["csv"],
        label_visibility="visible",
    )
with col2:
    st.markdown("<br>", unsafe_allow_html=True)  # Spacing
    if st.button("📤 Screen from CSV", use_container_width=True, disabled=not uploaded_file):
        if uploaded_file:
            st.info("Processing batch screening...")
            # TODO: Implement batch screening logic

st.markdown("---")

# Results Section
st.markdown("### Screening Results")

# Generate sample data (in production, this would come from API)
sample_markets = pd.DataFrame(
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
            "Durango, CO",
            "Park City, UT",
            "Coeur d'Alene, ID",
            "Grand Junction, CO",
            "Logan, UT",
        ],
        "State": ["CO", "CO", "ID", "UT", "CO", "UT", "CO", "UT", "ID", "CO", "CO", "UT", "ID", "CO", "UT"],
        "Composite": [87.2, 84.5, 83.8, 82.9, 82.1, 81.7, 80.3, 79.8, 78.5, 77.9, 76.5, 75.8, 74.2, 73.1, 72.5],
        "Supply": [95.1, 89.7, 88.2, 91.3, 78.3, 85.7, 82.1, 87.2, 83.5, 90.1, 85.3, 78.9, 80.5, 76.2, 82.8],
        "Jobs": [82.3, 85.2, 79.5, 80.1, 88.9, 82.4, 78.6, 73.5, 72.8, 79.2, 68.5, 71.3, 69.1, 70.5, 67.2],
        "Urban": [78.9, 75.1, 81.2, 79.5, 89.2, 87.3, 85.7, 82.1, 75.2, 68.3, 62.1, 58.9, 72.5, 74.3, 71.8],
        "Outdoor": [91.5, 88.3, 89.7, 87.2, 75.8, 78.5, 84.2, 85.3, 88.1, 90.5, 95.2, 96.1, 92.3, 87.5, 89.2],
        "Risk": [0.92, 0.95, 0.98, 0.91, 1.05, 0.94, 1.02, 0.96, 0.89, 0.93, 1.08, 0.99, 1.01, 1.12, 0.97],
    }
)

# Apply filters
if st.session_state.get("filters_applied", False) or search_term:
    filtered_markets = sample_markets.copy()

    # Search filter
    if search_term:
        filtered_markets = filtered_markets[
            filtered_markets["Market"].str.contains(search_term, case=False)
            | filtered_markets["State"].str.contains(search_term, case=False)
        ]

    # Score filters
    filters = st.session_state.get("filters", {})
    filtered_markets = filtered_markets[
        (filtered_markets["Supply"] >= filters.get("supply_min", 0))
        & (filtered_markets["Jobs"] >= filters.get("jobs_min", 0))
        & (filtered_markets["Urban"] >= filters.get("urban_min", 0))
        & (filtered_markets["Outdoor"] >= filters.get("outdoor_min", 0))
        & (filtered_markets["Risk"] <= filters.get("risk_max", 1.3))
        & (filtered_markets["Composite"] >= filters.get("composite_min", 0))
    ]

    results_count = len(filtered_markets)
    st.info(f"📊 Found **{results_count}** markets matching your criteria")
else:
    filtered_markets = sample_markets
    results_count = len(filtered_markets)
    st.info(f"📊 Showing **{results_count}** markets (apply filters to refine)")

# Sorting options
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown(f"**{results_count} Markets**")
with col2:
    sort_by = st.selectbox(
        "Sort by",
        ["Composite", "Supply", "Jobs", "Urban", "Outdoor", "Risk"],
        label_visibility="collapsed",
    )
with col3:
    sort_order = st.selectbox("Order", ["Descending", "Ascending"], label_visibility="collapsed")

# Sort dataframe
ascending = sort_order == "Ascending"
if sort_by == "Risk":
    filtered_markets = filtered_markets.sort_values(by=sort_by, ascending=not ascending)
else:
    filtered_markets = filtered_markets.sort_values(by=sort_by, ascending=ascending)

# Display results table with custom styling
st.markdown("#### Market Scores")

# Create formatted display
for idx, row in filtered_markets.iterrows():
    with st.container():
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([2, 1, 1, 1, 1, 1, 1, 1])

        with col1:
            st.markdown(
                f"**{row['Market']}**<br><span style='color: #6B7280; font-size: 12px;'>{row['State']}</span>",
                unsafe_allow_html=True,
            )

        with col2:
            score_color = get_score_color_hex(row["Composite"])
            st.markdown(
                f"<div style='text-align: center;'>"
                f"<span style='color: {score_color}; font-size: 24px; font-weight: 600;'>{row['Composite']:.1f}</span>"
                f"<br><span style='font-size: 11px; color: #6B7280;'>{get_score_label(row['Composite'])}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

        with col3:
            st.markdown(
                f"<div style='text-align: center; font-size: 14px;'>{row['Supply']:.1f}</div>",
                unsafe_allow_html=True,
            )

        with col4:
            st.markdown(
                f"<div style='text-align: center; font-size: 14px;'>{row['Jobs']:.1f}</div>",
                unsafe_allow_html=True,
            )

        with col5:
            st.markdown(
                f"<div style='text-align: center; font-size: 14px;'>{row['Urban']:.1f}</div>",
                unsafe_allow_html=True,
            )

        with col6:
            st.markdown(
                f"<div style='text-align: center; font-size: 14px;'>{row['Outdoor']:.1f}</div>",
                unsafe_allow_html=True,
            )

        with col7:
            risk_color = "#059669" if row["Risk"] < 1.0 else "#DC2626" if row["Risk"] > 1.1 else "#D97706"
            st.markdown(
                f"<div style='text-align: center; color: {risk_color}; font-weight: 600;'>{row['Risk']:.2f}x</div>",
                unsafe_allow_html=True,
            )

        with col8:
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("📍", key=f"view_{idx}", help="View Details"):
                    st.session_state.selected_market = row["Market"]
                    st.switch_page("pages/03_📍_Market_Details.py")
            with col_b:
                if st.button("➕", key=f"add_{idx}", help="Add to Portfolio"):
                    if "portfolio" not in st.session_state:
                        st.session_state.portfolio = []
                    st.session_state.portfolio.append(row.to_dict())
                    st.success(f"Added {row['Market']} to portfolio!")

        st.markdown("<hr style='margin: 8px 0;'>", unsafe_allow_html=True)

# Column headers
st.markdown(
    """
    <style>
    .column-headers {
        display: flex;
        font-size: 11px;
        font-weight: 600;
        color: #6B7280;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# Export options
st.markdown("#### Export Results")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📄 Export CSV", use_container_width=True):
        csv = filtered_markets.to_csv(index=False)
        st.download_button(
            "Download CSV",
            csv,
            "screening_results.csv",
            "text/csv",
            use_container_width=True,
        )

with col2:
    if st.button("📊 Export Excel", use_container_width=True):
        st.info("Excel export coming soon...")

with col3:
    if st.button("📑 Export PDF", use_container_width=True):
        st.info("PDF export coming soon...")

with col4:
    if st.button("💼 Add All to Portfolio", use_container_width=True):
        if "portfolio" not in st.session_state:
            st.session_state.portfolio = []
        for _, row in filtered_markets.iterrows():
            st.session_state.portfolio.append(row.to_dict())
        st.success(f"Added {len(filtered_markets)} markets to portfolio!")

