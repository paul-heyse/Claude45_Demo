"""Data Management page for Aker Investment Platform."""

import streamlit as st

from utils import format_percentage, get_api_client

st.set_page_config(
    page_title="Data Management - Aker Platform", page_icon="💾", layout="wide"
)

# Check authentication
if not st.session_state.get("logged_in", False):
    st.warning("⚠️ Please login to access data management")
    st.stop()

# Title
st.title("💾 Data Management")
st.markdown("### Manage Data Sources & Cache")

# Data source status
st.markdown("### Data Source Status")

data_sources = [
    {
        "name": "Census Bureau (ACS)",
        "status": "active",
        "last_update": "2 days ago",
        "cache_hit_rate": 89.2,
        "description": "American Community Survey demographic data",
    },
    {
        "name": "Bureau of Labor Statistics",
        "status": "active",
        "last_update": "5 days ago",
        "cache_hit_rate": 85.7,
        "description": "Employment and wage statistics (QCEW, CES, LAUS)",
    },
    {
        "name": "OpenStreetMap (Overpass)",
        "status": "active",
        "last_update": "Real-time",
        "cache_hit_rate": 92.3,
        "description": "Points of interest and geographic data",
    },
    {
        "name": "FEMA Flood Maps",
        "status": "warning",
        "last_update": "30 days ago",
        "cache_hit_rate": 78.5,
        "description": "National Flood Hazard Layer",
    },
    {
        "name": "EPA Air Quality (AQS)",
        "status": "active",
        "last_update": "1 day ago",
        "cache_hit_rate": 81.2,
        "description": "Air quality and pollution data",
    },
    {
        "name": "USGS Seismic Data",
        "status": "active",
        "last_update": "Real-time",
        "cache_hit_rate": 88.9,
        "description": "Earthquake hazard and risk data",
    },
]

for source in data_sources:
    with st.container():
        col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])

        with col1:
            status_icons = {"active": "✅", "warning": "⚠️", "error": "❌"}
            status_colors = {"active": "#059669", "warning": "#D97706", "error": "#DC2626"}

            icon = status_icons.get(source["status"], "ℹ️")
            color = status_colors.get(source["status"], "#6B7280")

            st.markdown(
                f"{icon} **{source['name']}**<br>"
                f"<span style='color: #6B7280; font-size: 12px;'>{source['description']}</span>",
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"<div style='text-align: center;'>"
                f"<span style='font-size: 12px; color: #6B7280;'>Last Update</span><br>"
                f"<span style='font-size: 14px;'>{source['last_update']}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

        with col3:
            st.markdown(
                f"<div style='text-align: center;'>"
                f"<span style='font-size: 12px; color: #6B7280;'>Cache Hit</span><br>"
                f"<span style='font-size: 14px; font-weight: 600;'>{source['cache_hit_rate']:.1f}%</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

        with col4:
            if st.button("🔄", key=f"refresh_{source['name']}", help="Refresh"):
                st.success(f"Refreshing {source['name']}...")

        with col5:
            if st.button("🗑️", key=f"clear_{source['name']}", help="Clear Cache"):
                st.warning(f"Cache cleared for {source['name']}")

        st.markdown("<hr style='margin: 8px 0;'>", unsafe_allow_html=True)

st.markdown("---")

# Cache statistics
st.markdown("### Cache Performance")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Overall Hit Rate", "87.3%", "+2.1%")

with col2:
    st.metric("Memory Cache", "198 MB / 256 MB", "77% used")

with col3:
    st.metric("SQLite Cache", "2.3 GB", "1,247 entries")

with col4:
    st.metric("Avg Latency", "12.5 ms", "-3.2 ms")

# Cache tier breakdown
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Cache Tier Performance")
    cache_tiers = {
        "Memory (Hot)": {"hits": 5420, "misses": 680, "latency": "0.8 ms"},
        "SQLite (Warm)": {"hits": 1250, "misses": 310, "latency": "8.2 ms"},
        "API (Cold)": {"hits": 0, "misses": 990, "latency": "245 ms"},
    }

    for tier, stats in cache_tiers.items():
        total = stats["hits"] + stats["misses"]
        hit_rate = (stats["hits"] / total * 100) if total > 0 else 0

        st.markdown(
            f"""
            <div style='padding: 12px; margin-bottom: 8px; border: 1px solid #E5E7EB; border-radius: 6px;'>
                <div style='display: flex; justify-content: space-between;'>
                    <strong>{tier}</strong>
                    <span style='color: #059669; font-weight: 600;'>{hit_rate:.1f}%</span>
                </div>
                <div style='font-size: 12px; color: #6B7280; margin-top: 4px;'>
                    Hits: {stats['hits']:,} | Misses: {stats['misses']:,} | Latency: {stats['latency']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

with col2:
    st.markdown("#### Cache by Data Source")
    source_cache = {
        "Census": {"size": "1.2 GB", "entries": 456, "hit_rate": 89.2},
        "BLS": {"size": "680 MB", "entries": 324, "hit_rate": 85.7},
        "OSM": {"size": "340 MB", "entries": 287, "hit_rate": 92.3},
        "FEMA": {"size": "85 MB", "entries": 124, "hit_rate": 78.5},
        "EPA": {"size": "45 MB", "entries": 56, "hit_rate": 81.2},
    }

    for source, stats in source_cache.items():
        st.markdown(
            f"""
            <div style='padding: 12px; margin-bottom: 8px; border: 1px solid #E5E7EB; border-radius: 6px;'>
                <div style='display: flex; justify-content: space-between;'>
                    <strong>{source}</strong>
                    <span>{stats['size']}</span>
                </div>
                <div style='font-size: 12px; color: #6B7280; margin-top: 4px;'>
                    Entries: {stats['entries']:,} | Hit Rate: {stats['hit_rate']:.1f}%
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("---")

# Cache warming
st.markdown("### Cache Warming")
st.markdown("Proactively load data into cache for frequently accessed markets.")

col1, col2 = st.columns([2, 1])

with col1:
    # Market selection for warming
    st.markdown("#### Select Markets to Warm")

    warm_option = st.radio(
        "Source",
        ["From Portfolio", "From CSV File", "Custom List"],
        horizontal=True,
    )

    if warm_option == "From Portfolio":
        portfolio = st.session_state.get("portfolio", [])
        if portfolio:
            warm_markets = [m.get("Market", "Unknown") for m in portfolio]
            st.info(f"📊 {len(warm_markets)} markets from portfolio: {', '.join(warm_markets[:3])}...")
        else:
            st.warning("Portfolio is empty")
            warm_markets = []
    elif warm_option == "From CSV File":
        uploaded_file = st.file_uploader("Upload market list (CSV)", type=["csv"])
        if uploaded_file:
            st.success("File uploaded successfully")
            warm_markets = ["Market1", "Market2", "Market3"]  # Mock
        else:
            warm_markets = []
    else:
        markets_input = st.text_area(
            "Enter markets (one per line)",
            placeholder="Boulder, CO\nDenver, CO\nFort Collins, CO",
        )
        warm_markets = [m.strip() for m in markets_input.split("\n") if m.strip()]

with col2:
    st.markdown("#### Data Sources")
    warm_census = st.checkbox("Census (ACS)", value=True)
    warm_bls = st.checkbox("BLS (Employment)", value=True)
    warm_osm = st.checkbox("OSM (POI)", value=True)
    warm_fema = st.checkbox("FEMA (Flood)", value=False)
    warm_epa = st.checkbox("EPA (Air Quality)", value=False)

    sources_to_warm = []
    if warm_census:
        sources_to_warm.append("census")
    if warm_bls:
        sources_to_warm.append("bls")
    if warm_osm:
        sources_to_warm.append("osm")
    if warm_fema:
        sources_to_warm.append("fema")
    if warm_epa:
        sources_to_warm.append("epa")

# Warming options
col1, col2, col3 = st.columns(3)
with col1:
    include_nearby = st.checkbox("Include nearby markets", value=False, help="Warm cache for markets within 50 miles")
with col2:
    parallel_requests = st.slider("Parallel requests", 1, 10, 4, help="Number of concurrent API requests")
with col3:
    rate_limit = st.slider("Rate limit (req/sec)", 1, 20, 10, help="Maximum requests per second")

# Start warming
if st.button(
    "🔥 Start Cache Warming",
    use_container_width=True,
    type="primary",
    disabled=not warm_markets or not sources_to_warm,
):
    with st.spinner("Warming cache..."):
        import time

        progress_text = st.empty()
        progress_bar = st.progress(0)

        total_items = len(warm_markets) * len(sources_to_warm)
        for i in range(total_items):
            market_idx = i // len(sources_to_warm)
            source_idx = i % len(sources_to_warm)

            if market_idx < len(warm_markets):
                progress_text.text(
                    f"Warming {warm_markets[market_idx]} - {sources_to_warm[source_idx]}..."
                )
            progress_bar.progress((i + 1) / total_items)
            time.sleep(0.1)

        st.success(
            f"✅ Cache warming complete!\n\n"
            f"Warmed {len(warm_markets)} markets across {len(sources_to_warm)} data sources.\n\n"
            f"Time taken: {total_items * 0.1:.1f} seconds"
        )

st.markdown("---")

# Cache management actions
st.markdown("### Cache Management")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔍 Inspect Cache", use_container_width=True):
        st.info("Cache inspection view coming soon...")

with col2:
    if st.button("📊 Cache Statistics", use_container_width=True):
        st.info("Detailed statistics view coming soon...")

with col3:
    if st.button("⚠️ Clear Expired", use_container_width=True):
        st.success("Cleared 127 expired cache entries (245 MB freed)")

with col4:
    if st.button("🗑️ Purge All Cache", use_container_width=True, type="secondary"):
        if st.checkbox("Confirm purge (this cannot be undone)"):
            st.warning("All cache data cleared (2.3 GB freed)")

