"""Help & Documentation page for Aker Investment Platform."""

import streamlit as st

st.set_page_config(page_title="Help - Aker Platform", page_icon="📚", layout="wide")

# Title
st.title("📚 Help & Documentation")
st.markdown("### Get Help with the Aker Investment Platform")

# Quick search
search_query = st.text_input(
    "🔍 Search help articles",
    placeholder="e.g., How to screen markets, understanding scores, API setup...",
)

if search_query:
    st.info(f"Searching for: '{search_query}' - Full search coming soon...")

# Help sections
tabs = st.tabs(
    [
        "🚀 Getting Started",
        "📖 User Guide",
        "❓ FAQ",
        "📊 Scoring Methodology",
        "🔑 API Setup",
        "💬 Contact Support",
    ]
)

# Tab 1: Getting Started
with tabs[0]:
    st.markdown("### Getting Started with Aker Platform")

    with st.expander("**1. Setting Up Your Account**", expanded=True):
        st.markdown(
            """
            #### Creating Your Profile
            1. Log in with your credentials
            2. Navigate to **Settings** → **User Profile**
            3. Complete your profile information
            4. Upload a profile photo (optional)

            #### Configuring API Keys
            1. Go to **Settings** → **API Keys**
            2. Enter your API keys for:
               - Census Bureau (required)
               - Bureau of Labor Statistics (required)
               - Other data sources (optional)
            3. Test each connection
            4. Save your settings

            **Note**: API keys are stored securely and never displayed in full.
            """
        )

    with st.expander("**2. Your First Market Screening**"):
        st.markdown(
            """
            #### Step-by-Step Screening
            1. Navigate to **🔍 Market Screening**
            2. Enter a city or state in the search bar
            3. Apply filters:
               - Supply Constraint Score
               - Innovation Jobs Score
               - Urban Convenience Score
               - Risk Multiplier
            4. Click **🔍 Screen** to see results
            5. Review the market list and scores
            6. Click **📍** to view detailed analysis
            7. Click **➕** to add markets to your portfolio

            #### Understanding the Results
            - **Composite Score**: Overall investment attractiveness (0-100)
            - **Component Scores**: Individual metrics breakdown
            - **Risk Multiplier**: Risk adjustment factor (0.7-1.3)
            """
        )

    with st.expander("**3. Building Your Portfolio**"):
        st.markdown(
            """
            #### Adding Markets
            1. Screen markets using filters
            2. Click **➕ Add to Portfolio** for promising markets
            3. Navigate to **💼 Portfolio** to manage

            #### Managing Your Portfolio
            - View all tracked markets in one place
            - Compare multiple markets side-by-side
            - Edit notes and status for each market
            - Remove markets you're no longer tracking
            - Export portfolio data (CSV, Excel, PDF)
            """
        )

    with st.expander("**4. Generating Reports**"):
        st.markdown(
            """
            #### Creating Professional Reports
            1. Go to **📊 Reports**
            2. Select a report template
            3. Choose markets to include
            4. Customize sections and options
            5. Click **Generate Report**
            6. Download in PDF, Excel, or HTML

            #### Available Templates
            - **Market Analysis**: Single market deep-dive
            - **Portfolio Summary**: All tracked markets
            - **Comparative Analysis**: Side-by-side comparison
            - **Risk Assessment**: Focused risk analysis
            - **Executive Summary**: High-level overview
            """
        )

# Tab 2: User Guide
with tabs[1]:
    st.markdown("### Complete User Guide")

    sections = [
        {
            "title": "Dashboard",
            "icon": "📊",
            "content": """
            The Dashboard provides a high-level overview of your portfolio and recent activity.

            **Key Features:**
            - Portfolio metrics (value, markets, cache performance)
            - Performance charts (6-month trend)
            - Top markets ranking
            - Geographic distribution
            - Recent activity feed
            - System health status
            """,
        },
        {
            "title": "Market Screening",
            "icon": "🔍",
            "content": """
            Use Market Screening to find investment opportunities based on your criteria.

            **Search Options:**
            - Text search (city, county, state)
            - Advanced filters (scores, risk, location)
            - Batch screening (upload CSV)

            **Filtering:**
            - Supply Constraint Score (0-100)
            - Innovation Jobs Score (0-100)
            - Urban Convenience Score (0-100)
            - Outdoor Access Score (0-100)
            - Risk Multiplier (0.7-1.3)
            - Composite Score (0-100)

            **Actions:**
            - View market details
            - Add to portfolio
            - Export results
            """,
        },
        {
            "title": "Market Details",
            "icon": "📍",
            "content": """
            Get comprehensive analysis for individual markets.

            **Sections:**
            1. **Score Overview**: Composite score and risk multiplier
            2. **Component Breakdown**: Radar chart of all scores
            3. **Detailed Scores**: Individual component analysis
            4. **Historical Trends**: Employment, permits, population, income
            5. **Demographics**: Population, economics, industry mix
            6. **Data Sources**: Transparency on data used

            **Interactive Charts:**
            - Radar chart for score comparison
            - Gauge chart for risk assessment
            - Line/bar charts for historical trends
            - Pie charts for demographics
            """,
        },
        {
            "title": "Portfolio Management",
            "icon": "💼",
            "content": """
            Track and manage your investment prospects.

            **Features:**
            - View all tracked markets
            - See status (Prospect, Committed, Active)
            - Add notes for each market
            - Compare multiple markets
            - Export portfolio data
            - View performance trends
            - Receive alerts on changes

            **Bulk Actions:**
            - Select multiple markets
            - Compare side-by-side
            - Generate reports
            - Export selection
            - Remove from portfolio
            """,
        },
        {
            "title": "Data Management",
            "icon": "💾",
            "content": """
            Manage data sources and cache performance.

            **Data Sources:**
            - View status of all APIs
            - Check last update times
            - Monitor cache hit rates
            - Refresh individual sources
            - Clear cache for specific sources

            **Cache Warming:**
            - Preload data for markets
            - Choose data sources to warm
            - Upload market list (CSV)
            - Schedule automatic warming
            - Monitor warming progress
            """,
        },
    ]

    for section in sections:
        with st.expander(f"{section['icon']} **{section['title']}**"):
            st.markdown(section["content"])

# Tab 3: FAQ
with tabs[2]:
    st.markdown("### Frequently Asked Questions")

    faqs = [
        {
            "q": "What data sources does Aker Platform use?",
            "a": """
            The platform integrates data from multiple authoritative sources:
            - **Census Bureau**: Demographics (ACS 5-Year)
            - **Bureau of Labor Statistics**: Employment (QCEW, CES, LAUS)
            - **Bureau of Economic Analysis**: Economic indicators
            - **OpenStreetMap**: Points of interest, geographic data
            - **FEMA**: Flood hazard maps
            - **USGS**: Seismic risk data
            - **EPA**: Air quality, environmental compliance
            - **NASA FIRMS**: Wildfire detection
            """,
        },
        {
            "q": "How is the composite score calculated?",
            "a": """
            The composite score (0-100) combines four component scores with configurable weights:

            **Default Weights:**
            - Supply Constraint: 35%
            - Innovation Jobs: 30%
            - Urban Convenience: 20%
            - Outdoor Access: 15%

            The composite is then adjusted by the risk multiplier to produce the final score.

            See the **Scoring Methodology** tab for detailed calculation methods.
            """,
        },
        {
            "q": "How often is data updated?",
            "a": """
            Update frequency varies by data source:

            **Real-time:**
            - OpenStreetMap POI data
            - USGS seismic data

            **Daily:**
            - EPA air quality data

            **Monthly:**
            - BLS employment statistics (monthly delay)

            **Annually:**
            - Census ACS data (released yearly)
            - FEMA flood maps (updated as needed)

            Cache TTL policies can be configured in **Settings** → **Cache Settings**.
            """,
        },
        {
            "q": "What do risk multipliers mean?",
            "a": """
            Risk multipliers (0.7-1.3) adjust scores based on hazards and constraints:

            **< 1.0**: Lower risk (positive adjustment)
            - Score is increased
            - Example: 0.90x means 10% risk discount

            **1.0**: Neutral risk (no adjustment)

            **> 1.0**: Higher risk (negative adjustment)
            - Score is decreased
            - Example: 1.15x means 15% risk premium

            **Extreme risks (>1.2x)** may trigger alerts or market exclusions.
            """,
        },
        {
            "q": "Can I customize scoring weights?",
            "a": """
            Yes! Custom weight configurations are coming soon in **Settings** → **Scoring Preferences**.

            You'll be able to:
            - Adjust component weights
            - Set minimum thresholds
            - Configure risk multiplier ranges
            - Save custom profiles
            - Share configurations with team
            """,
        },
        {
            "q": "How do I interpret score colors?",
            "a": """
            Score colors provide quick visual indicators:

            **Green (81-100)**: Excellent
            - Strong investment opportunity
            - All metrics above average

            **Blue (61-80)**: Good
            - Solid fundamentals
            - Generally attractive

            **Orange (41-60)**: Fair
            - Mixed signals
            - Requires deeper analysis

            **Red (0-40)**: Poor
            - Significant concerns
            - High risk or low potential
            """,
        },
    ]

    for faq in faqs:
        with st.expander(f"**Q: {faq['q']}**"):
            st.markdown(faq["a"])

# Tab 4: Scoring Methodology
with tabs[3]:
    st.markdown("### Scoring Methodology")
    st.info("📖 Detailed explanation of how market scores are calculated")

    with st.expander("**Supply Constraint Score (0-100)**", expanded=True):
        st.markdown(
            """
            Measures how constrained the housing supply is in a market.

            **Components:**
            1. **Permit Elasticity** (40%)
               - Building permit growth vs. population growth
               - Higher elasticity = less constrained

            2. **Topographic Constraints** (30%)
               - Slope, elevation, water bodies
               - Geographic limits on development

            3. **Regulatory Friction** (30%)
               - Permit timelines
               - Zoning restrictions
               - Environmental reviews

            **Calculation:**
            ```
            supply_score = (
                permit_elasticity * 0.40 +
                (100 - topographic_constraint) * 0.30 +
                (100 - regulatory_friction) * 0.30
            )
            ```

            **Interpretation:**
            - **High (>80)**: Very constrained supply → Potential for appreciation
            - **Low (<40)**: Abundant supply → May face downward price pressure
            """
        )

    with st.expander("**Innovation Jobs Score (0-100)**"):
        st.markdown(
            """
            Assesses the strength of high-wage innovation employment.

            **Components:**
            1. **Innovation Employment Share** (50%)
               - % of jobs in tech, professional services, finance
               - Industries with high productivity

            2. **Wage Premium** (30%)
               - Median wage vs. national average
               - Income growth rate

            3. **Job Mix Diversification** (20%)
               - Industry diversity (Shannon index)
               - Resilience to sector downturns

            **Calculation:**
            ```
            jobs_score = (
                innovation_share * 0.50 +
                wage_premium * 0.30 +
                diversification * 0.20
            )
            ```
            """
        )

    with st.expander("**Urban Convenience Score (0-100)**"):
        st.markdown(
            """
            Evaluates accessibility and urban amenities.

            **Components:**
            1. **15-Minute Accessibility** (40%)
               - % of population within 15-min walk of amenities
               - Measured using OpenStreetMap POI data

            2. **Retail & Services Health** (35%)
               - Density of restaurants, cafes, shops
               - Healthcare facilities
               - Entertainment venues

            3. **Transit Quality** (25%)
               - Public transit coverage
               - Walkability index
               - Bike infrastructure

            **15-Minute Amenities Include:**
            - Grocery stores
            - Restaurants & cafes
            - Parks & recreation
            - Healthcare
            - Schools
            - Retail
            """
        )

    with st.expander("**Outdoor Access Score (0-100)**"):
        st.markdown(
            """
            Measures proximity to outdoor recreation.

            **Components:**
            1. **Trail Density** (35%)
               - Miles of hiking/biking trails per capita
               - Quality and variety of trails

            2. **Public Lands Access** (35%)
               - Distance to national forests, parks, BLM land
               - % of county in public lands

            3. **Ski Resorts & Recreation** (30%)
               - Proximity to ski areas
               - Water recreation (lakes, rivers)
               - Other outdoor amenities

            **Amenities Scored:**
            - Hiking trails
            - Mountain biking
            - Ski resorts (within 50 miles)
            - National parks
            - Lakes & rivers
            - Rock climbing areas
            """
        )

    with st.expander("**Risk Multiplier (0.7-1.3)**"):
        st.markdown(
            """
            Adjusts composite score based on hazards.

            **Risk Factors:**
            1. **Wildfire Risk**
               - WUI classification
               - Historical fire data
               - Wildfire Hazard Potential

            2. **Flood Risk**
               - FEMA flood zones
               - 100-year floodplain
               - Historical flooding

            3. **Seismic Risk**
               - USGS seismic hazard maps
               - Earthquake probability
               - Building code compliance

            4. **Other Hazards**
               - Hail risk
               - Snow load
               - Radon levels

            5. **Regulatory Friction**
               - Permit timelines
               - Development restrictions

            6. **Water Stress**
               - Drought risk
               - Water rights issues

            **Calculation:**
            ```
            risk_multiplier = 1.0
            for each risk factor:
                if extreme: exclude market
                else: risk_multiplier += factor_weight

            final_score = composite_score * (2.0 - risk_multiplier)
            ```
            """
        )

# Tab 5: API Setup
with tabs[4]:
    st.markdown("### API Configuration Guide")

    with st.expander("**Census Bureau API**", expanded=True):
        st.markdown(
            """
            #### Getting Your API Key
            1. Visit: [api.census.gov/data/key_signup.html](https://api.census.gov/data/key_signup.html)
            2. Fill out the registration form
            3. Verify your email address
            4. API key will be sent via email

            #### Configuring in Aker Platform
            1. Go to **Settings** → **API Keys**
            2. Find "Census Bureau"
            3. Paste your API key
            4. Click **Test** to verify connection
            5. Click **Save**

            #### Data Retrieved
            - American Community Survey (ACS) 5-Year estimates
            - Population demographics
            - Income statistics
            - Housing data
            """
        )

    with st.expander("**Bureau of Labor Statistics API**"):
        st.markdown(
            """
            #### Registration
            1. Visit: [www.bls.gov/developers/](https://www.bls.gov/developers/)
            2. Click "Request API Key"
            3. Complete registration form
            4. Receive key via email

            #### Data Retrieved
            - QCEW (Quarterly Census of Employment and Wages)
            - CES (Current Employment Statistics)
            - LAUS (Local Area Unemployment Statistics)
            """
        )

# Tab 6: Contact Support
with tabs[5]:
    st.markdown("### Contact Support")

    st.markdown("#### Get Help from Our Team")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("**Submit a Support Request**")

        subject_type = st.selectbox(
            "Subject",
            [
                "Bug Report",
                "Feature Request",
                "Data Question",
                "API Issue",
                "General Question",
                "Other",
            ],
        )

        subject = st.text_input("Subject line", placeholder="Brief description of your issue")

        message = st.text_area(
            "Message",
            placeholder="Please provide as much detail as possible...",
            height=200,
        )

        attachment = st.file_uploader(
            "Attach file (optional)",
            type=["png", "jpg", "pdf", "csv", "xlsx"],
        )

        if st.button("📤 Submit Request", type="primary", use_container_width=True):
            st.success(
                "✅ Support request submitted successfully!\n\n"
                "We typically respond within 24 hours.\n"
                "A confirmation email has been sent to your registered email address."
            )

    with col2:
        st.markdown("**Other Support Options**")

        st.markdown(
            """
            📧 **Email**
            support@aker-platform.com

            💬 **Live Chat**
            Available Mon-Fri, 9am-5pm MT

            📞 **Phone**
            +1 (555) 123-4567

            📚 **Documentation**
            docs.aker-platform.com

            🐛 **GitHub Issues**
            github.com/aker/platform/issues
            """
        )

        st.markdown("---")

        st.markdown("**Response Times**")
        st.markdown(
            """
            - Critical: < 4 hours
            - High: < 24 hours
            - Normal: < 48 hours
            - Low: < 72 hours
            """
        )

