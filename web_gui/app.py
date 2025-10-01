"""
Aker Investment Platform - Web GUI Main Application.

Multi-page Streamlit application for real estate investment analysis.
"""

from pathlib import Path

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Aker Investment Platform",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/aker/platform",
        "Report a bug": "https://github.com/aker/platform/issues",
        "About": "# Aker Investment Platform\nReal Estate Investment Analysis",
    },
)

# Load custom CSS
css_file = Path(__file__).parent / "assets" / "styles.css"
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "portfolio" not in st.session_state:
    st.session_state.portfolio = []
if "selected_market" not in st.session_state:
    st.session_state.selected_market = None
if "filters" not in st.session_state:
    st.session_state.filters = {}

# Sidebar
with st.sidebar:
    st.image(
        "https://via.placeholder.com/150x50/1E40AF/FFFFFF?text=AKER",
        use_column_width=True,
    )
    st.title("Navigation")
    st.markdown("---")

    # Login status
    if st.session_state.logged_in:
        st.success(f"✓ Logged in as: {st.session_state.get('username', 'User')}")
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()
    else:
        st.warning("⚠️ Not logged in")
        if st.button("Login", use_container_width=True):
            # Redirect to login (would be handled by authentication)
            st.session_state.logged_in = True
            st.session_state.username = "demo@aker.com"
            st.rerun()

    st.markdown("---")

    # Quick stats in sidebar
    if st.session_state.logged_in:
        st.subheader("Quick Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Markets", len(st.session_state.portfolio))
        with col2:
            st.metric("Cache Hit", "87.3%")

# Main content
st.title("🏠 Aker Investment Platform")
st.markdown("### Real Estate Market Analysis & Investment Screening")

# Welcome message
if not st.session_state.logged_in:
    st.info(
        """
        👋 **Welcome to the Aker Investment Platform**

        Please login to access market screening, portfolio management, and reporting features.

        **Quick Links:**
        - 🔍 [Market Screening](#) - Find investment opportunities
        - 📊 [Dashboard](#) - View portfolio performance
        - 📍 [Market Details](#) - Analyze specific markets
        """
    )
else:
    # Quick actions
    st.markdown("### Quick Actions")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🔍 Screen Markets", use_container_width=True):
            st.switch_page("pages/02_🔍_Market_Screening.py")

    with col2:
        if st.button("📊 View Dashboard", use_container_width=True):
            st.switch_page("pages/01_📊_Dashboard.py")

    with col3:
        if st.button("💼 Portfolio", use_container_width=True):
            st.switch_page("pages/04_💼_Portfolio.py")

    with col4:
        if st.button("📋 Generate Report", use_container_width=True):
            st.switch_page("pages/05_📊_Reports.py")

    st.markdown("---")

    # Recent activity
    st.subheader("📅 Recent Activity")
    st.markdown(
        """
        - **Today, 2:30 PM** - Added Boulder, CO to portfolio
        - **Today, 11:45 AM** - Generated report for Fort Collins, CO
        - **Yesterday, 4:20 PM** - Screened 127 markets in Colorado
        - **Yesterday, 10:15 AM** - Updated cache for BLS data
        """
    )

    st.markdown("---")

    # System status
    st.subheader("🔧 System Status")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Cache Hit Rate", "87.3%", "↑ 2.1%")
    with col2:
        st.metric("API Status", "Healthy", "")
    with col3:
        st.metric("Data Sources", "12", "All Online")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #6B7280; font-size: 12px;'>
        <p>Aker Investment Platform v1.0.0 | © 2024 Aker Capital Management</p>
        <p>Data Sources: Census Bureau, BLS, OpenStreetMap, FEMA, EPA</p>
    </div>
    """,
    unsafe_allow_html=True,
)
