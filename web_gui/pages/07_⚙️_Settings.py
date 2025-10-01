"""Settings page for Aker Investment Platform."""

import streamlit as st

st.set_page_config(page_title="Settings - Aker Platform", page_icon="⚙️", layout="wide")

# Check authentication
if not st.session_state.get("logged_in", False):
    st.warning("⚠️ Please login to access settings")
    st.stop()

# Title
st.title("⚙️ Settings")
st.markdown("### Configuration & Preferences")

# Settings tabs
tabs = st.tabs(
    [
        "👤 User Profile",
        "🔑 API Keys",
        "💾 Cache Settings",
        "🎨 Display",
        "📤 Export",
        "🔔 Notifications",
    ]
)

# Tab 1: User Profile
with tabs[0]:
    st.markdown("### User Profile")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("#### Profile Picture")
        st.image(
            "https://via.placeholder.com/150/1E40AF/FFFFFF?text=User",
            width=150,
        )
        if st.button("Upload New Photo"):
            st.info("Photo upload coming soon...")

    with col2:
        st.markdown("#### Profile Information")

        name = st.text_input("Full Name", value="Demo User")
        email = st.text_input("Email", value="demo@aker.com", disabled=True)
        organization = st.text_input("Organization", value="Aker Capital Management")
        role = st.text_input("Role/Title", value="Investment Analyst")

        if st.button("💾 Save Profile", type="primary"):
            st.success("Profile updated successfully!")

    st.markdown("---")
    st.markdown("### Account Security")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Change Password")
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Update Password"):
            if new_password == confirm_password:
                st.success("Password updated successfully!")
            else:
                st.error("Passwords do not match")

    with col2:
        st.markdown("#### Two-Factor Authentication")
        st.info("2FA is currently disabled")
        if st.button("Enable 2FA"):
            st.info("2FA setup coming soon...")

        st.markdown("#### Active Sessions")
        st.markdown(
            """
            - **Current Session**: Desktop (192.168.1.100)
            - Started: Today at 9:30 AM
            """
        )

# Tab 2: API Keys
with tabs[1]:
    st.markdown("### API Configuration")
    st.info("ℹ️ API keys are stored securely and never displayed in full.")

    api_keys = [
        {"name": "Census Bureau", "key": "census_api_key", "status": "✅ Connected"},
        {"name": "Bureau of Labor Statistics", "key": "bls_api_key", "status": "✅ Connected"},
        {"name": "Bureau of Economic Analysis", "key": "bea_api_key", "status": "✅ Connected"},
        {"name": "EPA Air Quality", "key": "epa_api_key", "status": "⚠️ Not Configured"},
        {"name": "NASA FIRMS", "key": "nasa_api_key", "status": "⚠️ Not Configured"},
    ]

    for api in api_keys:
        with st.expander(f"{api['name']} - {api['status']}"):
            col1, col2 = st.columns([3, 1])

            with col1:
                key_value = st.text_input(
                    f"{api['name']} API Key",
                    value="••••••••••••••••" if "Connected" in api["status"] else "",
                    type="password",
                    key=api["key"],
                )

            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Test", key=f"test_{api['key']}", use_container_width=True):
                    st.success("✅ Connection successful!")

            if st.button("Save Key", key=f"save_{api['key']}"):
                st.success(f"{api['name']} API key saved!")

    st.markdown("---")
    st.markdown("### API Documentation")
    st.markdown(
        """
        **Required API Keys:**
        - **Census Bureau**: Get your key at [api.census.gov/data/key_signup.html](https://api.census.gov/data/key_signup.html)
        - **BLS**: Register at [www.bls.gov/developers/](https://www.bls.gov/developers/)
        - **BEA**: Request at [apps.bea.gov/API/signup/](https://apps.bea.gov/API/signup/)
        """
    )

# Tab 3: Cache Settings
with tabs[2]:
    st.markdown("### Cache Configuration")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Memory Cache")
        memory_size = st.slider("Memory cache size (MB)", 64, 512, 256, 64)
        st.metric("Current Usage", "198 MB / 256 MB", "77% used")

        st.markdown("#### SQLite Cache")
        sqlite_path = st.text_input("Cache database path", value="./cache/aker_cache.db")

    with col2:
        st.markdown("#### TTL Policies (Time to Live)")

        st.markdown("**Static Data:**")
        static_ttl = st.number_input("Static data TTL (days)", 1, 365, 365)

        st.markdown("**Semi-Static Data:**")
        semi_static_ttl = st.number_input("Semi-static TTL (days)", 1, 90, 30)

        st.markdown("**Dynamic Data:**")
        dynamic_ttl = st.number_input("Dynamic TTL (days)", 1, 30, 7)

        st.markdown("**Real-time Data:**")
        realtime_ttl = st.number_input("Real-time TTL (hours)", 1, 24, 1)

    st.markdown("---")
    st.markdown("### Advanced Cache Options")

    col1, col2 = st.columns(2)

    with col1:
        enable_compression = st.checkbox("Enable compression (>10KB responses)", value=True)
        compression_level = st.slider("Compression level", 0, 9, 6) if enable_compression else 6

    with col2:
        enable_warming = st.checkbox("Enable automatic cache warming", value=True)
        warming_schedule = st.selectbox("Warming schedule", ["Daily at 2 AM", "Weekly on Sunday", "Manual only"])

    if st.button("💾 Save Cache Settings", type="primary"):
        st.success("Cache settings saved successfully!")

# Tab 4: Display Preferences
with tabs[3]:
    st.markdown("### Display Preferences")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Theme & Layout")
        theme = st.selectbox("Theme", ["Light", "Dark", "Auto (System)"])
        map_style = st.selectbox("Default map style", ["Street", "Satellite", "Terrain"])

        st.markdown("#### Numbers & Dates")
        number_format = st.selectbox("Number format", ["US (1,234.56)", "European (1.234,56)"])
        date_format = st.selectbox("Date format", ["MM/DD/YYYY", "DD/MM/YYYY", "YYYY-MM-DD"])

    with col2:
        st.markdown("#### Tables & Charts")
        results_per_page = st.selectbox("Results per page", [25, 50, 100, 200])
        default_chart_style = st.selectbox("Chart style", ["Professional", "Minimal", "Colorful"])

        st.markdown("#### Accessibility")
        high_contrast = st.checkbox("High contrast mode")
        large_text = st.checkbox("Larger text size")

    if st.button("💾 Save Display Settings", type="primary"):
        st.success("Display settings saved!")

# Tab 5: Export Preferences
with tabs[4]:
    st.markdown("### Export Preferences")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Default Export Format")
        default_format = st.selectbox("Export format", ["CSV", "Excel", "PDF"])

        st.markdown("#### Export Options")
        include_metadata = st.checkbox("Include metadata in exports", value=True)
        include_filters = st.checkbox("Include applied filters", value=True)
        include_timestamp = st.checkbox("Add timestamp to filename", value=True)

    with col2:
        st.markdown("#### PDF Report Settings")
        st.image("https://via.placeholder.com/200x80/1E40AF/FFFFFF?text=Logo", width=200)
        if st.button("Upload Company Logo"):
            st.info("Logo upload coming soon...")

        footer_text = st.text_area(
            "Report footer text",
            value="Aker Capital Management | Confidential",
            height=80,
        )

    if st.button("💾 Save Export Settings", type="primary"):
        st.success("Export settings saved!")

# Tab 6: Notifications
with tabs[5]:
    st.markdown("### Notification Preferences")

    st.markdown("#### Email Notifications")
    email_enabled = st.checkbox("Enable email notifications", value=True)

    if email_enabled:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Portfolio Alerts**")
            notify_score_change = st.checkbox("Score changes (>5 points)", value=True)
            notify_new_risk = st.checkbox("New risk factors detected", value=True)
            notify_data_update = st.checkbox("Data source updates", value=False)

        with col2:
            st.markdown("**Report Generation**")
            notify_report_complete = st.checkbox("Report generation complete", value=True)
            notify_report_failed = st.checkbox("Report generation failed", value=True)
            notify_scheduled_reports = st.checkbox("Scheduled report reminders", value=False)

    st.markdown("---")
    st.markdown("#### Digest Email")
    col1, col2 = st.columns(2)

    with col1:
        digest_enabled = st.checkbox("Send daily digest email", value=True)
        digest_time = st.time_input("Digest time", value=None)

    with col2:
        st.markdown("**Digest Contents**")
        digest_portfolio = st.checkbox("Portfolio summary", value=True)
        digest_alerts = st.checkbox("New alerts", value=True)
        digest_recommendations = st.checkbox("Investment recommendations", value=False)

    if st.button("💾 Save Notification Settings", type="primary"):
        st.success("Notification settings saved!")

