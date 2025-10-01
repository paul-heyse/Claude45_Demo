"""Reports page for Aker Investment Platform."""

from datetime import datetime

import streamlit as st

from utils import get_api_client

st.set_page_config(page_title="Reports - Aker Platform", page_icon="📊", layout="wide")

# Check authentication
if not st.session_state.get("logged_in", False):
    st.warning("⚠️ Please login to access reports")
    st.stop()

# Title
st.title("📊 Reports & Export")
st.markdown("### Generate Professional Investment Reports")

# Report templates
st.markdown("### Report Templates")

templates = [
    {
        "name": "Market Analysis Report",
        "icon": "📍",
        "description": "Comprehensive analysis for a single market including scores, demographics, trends, and risk assessment.",
        "pages": "15-20 pages",
        "markets": "Single market",
    },
    {
        "name": "Portfolio Summary Report",
        "icon": "💼",
        "description": "Executive summary of all tracked markets with performance metrics and comparative analysis.",
        "pages": "10-15 pages",
        "markets": "All portfolio markets",
    },
    {
        "name": "Comparative Market Analysis",
        "icon": "📊",
        "description": "Side-by-side comparison of 2-5 markets with detailed score breakdowns and rankings.",
        "pages": "8-12 pages per market",
        "markets": "2-5 markets",
    },
    {
        "name": "Risk Assessment Report",
        "icon": "⚠️",
        "description": "Focused analysis of risk factors including wildfire, flood, seismic, and regulatory risks.",
        "pages": "10-12 pages",
        "markets": "Single or multiple",
    },
    {
        "name": "Executive Summary",
        "icon": "📄",
        "description": "High-level overview with key metrics, top recommendations, and market highlights.",
        "pages": "2-3 pages",
        "markets": "Portfolio or selection",
    },
]

col1, col2, col3 = st.columns(3)

for idx, template in enumerate(templates):
    col = [col1, col2, col3][idx % 3]
    with col:
        with st.container():
            st.markdown(
                f"""
                <div style='padding: 20px; border: 2px solid #E5E7EB; border-radius: 8px; height: 280px;'>
                    <div style='font-size: 48px; text-align: center;'>{template['icon']}</div>
                    <h4 style='text-align: center; margin: 8px 0;'>{template['name']}</h4>
                    <p style='color: #6B7280; font-size: 14px;'>{template['description']}</p>
                    <div style='margin-top: 12px; font-size: 12px; color: #6B7280;'>
                        <div>📄 {template['pages']}</div>
                        <div>🎯 {template['markets']}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.button(
                f"Select {template['name']}",
                key=f"template_{idx}",
                use_container_width=True,
                type="secondary" if idx > 0 else "primary",
            )

st.markdown("---")

# Report configuration
st.markdown("### Configure Report")

selected_template = st.selectbox(
    "Report Template",
    [t["name"] for t in templates],
    help="Select a report template to customize",
)

# Market selection
st.markdown("#### Select Markets")
col1, col2 = st.columns([2, 1])

with col1:
    # Get portfolio markets
    portfolio = st.session_state.get("portfolio", [])
    if portfolio:
        market_options = [m.get("Market", "Unknown") for m in portfolio]
        selected_markets = st.multiselect(
            "Markets to include",
            market_options,
            default=market_options[:1] if market_options else [],
            help="Select one or more markets for the report",
        )
    else:
        st.info("No markets in portfolio. Add markets from the screening page.")
        selected_markets = []

with col2:
    st.markdown("**Quick Selection**")
    if st.button("Select All", use_container_width=True):
        st.session_state.selected_markets = market_options
    if st.button("Clear Selection", use_container_width=True):
        st.session_state.selected_markets = []

# Report sections
st.markdown("#### Report Sections")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Core Sections**")
    include_exec_summary = st.checkbox("Executive Summary", value=True)
    include_methodology = st.checkbox("Methodology", value=True)
    include_scores = st.checkbox("Score Analysis", value=True)
    include_demographics = st.checkbox("Demographics", value=True)

with col2:
    st.markdown("**Data Sections**")
    include_trends = st.checkbox("Historical Trends", value=True)
    include_risk = st.checkbox("Risk Assessment", value=True)
    include_maps = st.checkbox("Maps & Visualizations", value=True)
    include_comparisons = st.checkbox("Market Comparisons", value=len(selected_markets) > 1)

with col3:
    st.markdown("**Appendix**")
    include_sources = st.checkbox("Data Sources", value=True)
    include_glossary = st.checkbox("Glossary", value=False)
    include_raw_data = st.checkbox("Raw Data Tables", value=False)
    include_methodology_detail = st.checkbox("Detailed Methodology", value=False)

# Report options
st.markdown("#### Report Options")

col1, col2, col3 = st.columns(3)

with col1:
    date_range = st.selectbox(
        "Historical Data Range",
        ["Last 5 Years", "Last 10 Years", "All Available"],
        help="Time range for historical trend analysis",
    )

with col2:
    detail_level = st.selectbox(
        "Detail Level",
        ["Executive (High-level)", "Standard", "Detailed (Technical)"],
        index=1,
        help="Amount of detail and technical depth",
    )

with col3:
    chart_style = st.selectbox(
        "Chart Style",
        ["Professional", "Minimal", "Colorful"],
        help="Visual style for charts and graphs",
    )

st.markdown("---")

# Report preview
st.markdown("### Report Preview")

if selected_markets:
    st.info(
        f"📄 **Report Preview**: {selected_template} for {len(selected_markets)} market(s)\n\n"
        f"**Markets**: {', '.join(selected_markets)}\n\n"
        f"**Estimated Pages**: {len(selected_markets) * 15} pages\n\n"
        f"**Est. Generation Time**: {len(selected_markets) * 30} seconds"
    )

    # Preview structure
    with st.expander("📋 Report Structure Preview", expanded=False):
        st.markdown(
            f"""
            ### {selected_template}

            **1. Cover Page**
            - Report title and date
            - Markets included
            - Aker branding

            **2. Table of Contents**
            - Navigable sections

            **3. Executive Summary** {'✓' if include_exec_summary else '✗'}
            - Key findings
            - Investment recommendations
            - Risk highlights

            **4. Methodology** {'✓' if include_methodology else '✗'}
            - Scoring approach
            - Data sources
            - Calculation methods

            **5. Market Analysis** {'✓' if include_scores else '✗'}
            - Composite scores
            - Component breakdowns
            - Percentile rankings

            **6. Demographics & Economics** {'✓' if include_demographics else '✗'}
            - Population trends
            - Income statistics
            - Employment data

            **7. Historical Trends** {'✓' if include_trends else '✗'}
            - Employment growth
            - Building permits
            - Population changes

            **8. Risk Assessment** {'✓' if include_risk else '✗'}
            - Risk multipliers
            - Hazard analysis
            - Mitigation factors

            **9. Maps & Visualizations** {'✓' if include_maps else '✗'}
            - Geographic maps
            - Charts and graphs
            - Score visualizations

            **10. Appendix**
            - Data sources {'✓' if include_sources else '✗'}
            - Glossary {'✓' if include_glossary else '✗'}
            - Raw data {'✓' if include_raw_data else '✗'}
            """
        )
else:
    st.warning("⚠️ Please select at least one market to generate a report")

st.markdown("---")

# Generate report
st.markdown("### Generate Report")

col1, col2, col3 = st.columns(3)

with col1:
    output_format = st.radio(
        "Output Format",
        ["PDF", "Excel", "HTML"],
        help="File format for generated report",
    )

with col2:
    include_logo = st.checkbox("Include Company Logo", value=True)
    include_footer = st.checkbox("Include Page Numbers", value=True)

with col3:
    email_report = st.checkbox("Email when complete", value=False)
    if email_report:
        email_address = st.text_input("Email address", placeholder="user@example.com")

# Generate button
if st.button(
    f"📄 Generate {output_format} Report",
    use_container_width=True,
    type="primary",
    disabled=not selected_markets,
):
    with st.spinner(f"Generating {output_format} report..."):
        import time

        # Simulate report generation
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.02)
            progress_bar.progress(i + 1)

        st.success(
            f"✅ Report generated successfully!\n\n"
            f"**File**: {selected_template.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.{output_format.lower()}\n\n"
            f"**Size**: {len(selected_markets) * 2.5:.1f} MB"
        )

        # Mock download button
        st.download_button(
            f"📥 Download {output_format} Report",
            data="Mock report content",
            file_name=f"aker_report_{datetime.now().strftime('%Y%m%d')}.{output_format.lower()}",
            mime=f"application/{output_format.lower()}",
            use_container_width=True,
        )

st.markdown("---")

# Report history
st.markdown("### Recent Reports")

report_history = [
    {
        "name": "Boulder_Market_Analysis_20241201.pdf",
        "date": "2024-12-01 14:30",
        "markets": "Boulder, CO",
        "size": "3.2 MB",
        "format": "PDF",
    },
    {
        "name": "Portfolio_Summary_20241128.xlsx",
        "date": "2024-11-28 09:15",
        "markets": "4 markets",
        "size": "8.5 MB",
        "format": "Excel",
    },
    {
        "name": "Risk_Assessment_20241125.pdf",
        "date": "2024-11-25 16:45",
        "markets": "Fort Collins, CO; Denver, CO",
        "size": "5.1 MB",
        "format": "PDF",
    },
]

for report in report_history:
    col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 1, 1, 1, 1])

    with col1:
        st.markdown(f"**{report['name']}**")
    with col2:
        st.markdown(f"<span style='color: #6B7280; font-size: 12px;'>{report['markets']}</span>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<span style='font-size: 12px;'>{report['format']}</span>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<span style='font-size: 12px;'>{report['size']}</span>", unsafe_allow_html=True)
    with col5:
        st.button("📥", key=f"dl_{report['name']}", help="Download")
    with col6:
        st.button("🗑️", key=f"del_{report['name']}", help="Delete")

    st.markdown("<hr style='margin: 4px 0;'>", unsafe_allow_html=True)

