# Web GUI Module - Overview

## Purpose

The Web GUI module provides a comprehensive multi-page graphical user interface for the Aker Investment Platform, enabling users to screen markets, analyze properties, manage portfolios, and generate reports through an intuitive web-based interface.

## Key Features

### 🏠 Dashboard
- Portfolio overview with key metrics
- Performance charts and visualizations
- Geographic distribution map
- Quick action buttons
- Recent activity feed

### 🔍 Market Screening
- Advanced search with autocomplete
- Multi-criteria filtering (scores, risk, location)
- Sortable results table
- Batch screening via CSV upload
- Export results (CSV, Excel, PDF)

### 📍 Market Details
- Comprehensive market analysis
- Interactive score breakdowns (radar chart)
- Risk assessment visualizations
- Interactive maps with layers
- Historical trend charts
- Data source transparency

### 💼 Portfolio Management
- Track multiple markets
- Add/remove/organize markets
- Compare markets side-by-side
- Portfolio-level analytics
- Notes and status tracking
- Alert notifications

### 📊 Reports
- Multiple report templates
- Custom report builder
- PDF generation with charts
- Excel exports with formulas
- Scheduled reports
- Report history management

### ⚙️ Settings & Configuration
- API key management
- Cache configuration
- Display preferences
- Export options
- User profile management

### 📚 Help & Documentation
- Interactive tutorials
- Comprehensive user guides
- FAQ section
- Contact support form

## Technology Stack

### Frontend
- **Framework**: Streamlit (MVP) → Dash/React (Production)
- **Charts**: Plotly (interactive visualizations)
- **Maps**: Mapbox GL JS or Folium
- **Tables**: AG Grid or built-in DataFrames
- **Styling**: Custom CSS with professional theme

### Backend Integration
- **API**: REST API (FastAPI)
- **Authentication**: OAuth/JWT tokens
- **Session**: Browser cookies + backend validation
- **Data**: JSON responses from Python backend

### Export & Reporting
- **PDF**: ReportLab or WeasyPrint
- **Excel**: openpyxl or xlsxwriter
- **CSV**: pandas.to_csv
- **Charts**: Rendered as high-res images in PDFs

## Architecture

```
┌─────────────────────────────────────────────┐
│           Browser (User Interface)           │
│  ┌─────────┐  ┌─────────┐  ┌──────────┐    │
│  │Dashboard│  │Screening│  │Portfolio │    │
│  └────┬────┘  └────┬────┘  └────┬─────┘    │
└───────┼───────────┼──────────────┼──────────┘
        │           │              │
        └───────────┴──────────────┘
                    │
        ┌───────────▼──────────────┐
        │   REST API (FastAPI)     │
        │  ┌──────────────────┐    │
        │  │ Authentication   │    │
        │  │ Data Endpoints   │    │
        │  │ Cache Management │    │
        │  │ Report Generation│    │
        │  └──────────────────┘    │
        └───────────┬──────────────┘
                    │
        ┌───────────▼──────────────┐
        │   Python Backend         │
        │  ┌──────────────────┐    │
        │  │ Scoring Engine   │    │
        │  │ Market Analysis  │    │
        │  │ Risk Assessment  │    │
        │  │ Data Integration │    │
        │  │ Cache System     │    │
        │  └──────────────────┘    │
        └──────────────────────────┘
```

## Page Flow

```
Login → Dashboard → [Market Screening] → Market Details → Add to Portfolio
           ↓              ↓                     ↓              ↓
        Settings    Export Results       View on Map      Portfolio
           ↓              ↓                     ↓              ↓
     Configure API   Generate Report    Historical Trends  Compare Markets
```

## Design Principles

### 1. Data-First Design
- Prioritize clear presentation of metrics
- Use color-coding for quick interpretation
- Provide context (percentiles, historical trends)
- Show data provenance (sources, update times)

### 2. Progressive Disclosure
- Show essential information first
- Expand details on demand (accordions, modals)
- Guided workflows for complex tasks
- Tooltips for technical terms

### 3. Responsive & Accessible
- Mobile-friendly layouts
- Touch-optimized controls
- Keyboard navigation support
- Screen reader compatible
- WCAG 2.1 AA compliance

### 4. Performance
- Lazy loading for large datasets
- Caching at multiple levels
- Progressive rendering
- Skeleton screens during load

### 5. Trust & Professionalism
- Conservative color palette (blues, grays)
- Clear typography (Inter, JetBrains Mono)
- Consistent spacing and alignment
- Professional chart styling

## Color Scheme

```css
Primary (Blue):      #1E40AF  /* Main actions, links */
Secondary (Green):   #059669  /* Success, positive */
Warning (Amber):     #D97706  /* Alerts, caution */
Danger (Red):        #DC2626  /* Errors, high risk */
Neutral (Gray):      #6B7280  /* Text, borders */
Background:          #F9FAFB  /* Page background */

Score Colors:
  0-40:  #DC2626 (Red)     - Poor
  41-60: #D97706 (Orange)  - Fair
  61-80: #2563EB (Blue)    - Good
  81-100:#059669 (Green)   - Excellent
```

## Implementation Phases

### Phase 1: MVP (2-3 weeks)
**Goal**: Basic functionality for market screening and analysis

- ✅ Streamlit app structure
- ✅ Dashboard with basic metrics
- ✅ Market screening (search, filter, results)
- ✅ Market details (scores, basic charts)
- ✅ Settings (API configuration)
- ✅ Basic authentication

**Deliverable**: Functional web app for internal testing

### Phase 2: Portfolio & Reports (3-4 weeks)
**Goal**: Portfolio management and reporting capabilities

- Portfolio page (add, track, compare)
- Reports page (templates, generation)
- PDF export with charts
- Data management (cache inspection)
- Help documentation

**Deliverable**: Feature-complete MVP

### Phase 3: Enhancement (4-6 weeks)
**Goal**: Production-ready with optimizations

- Mobile optimization
- Interactive maps (Mapbox)
- Advanced visualizations
- Scheduled reports
- Performance tuning
- Security hardening
- Automated testing
- Deployment (Docker, Cloud)

**Deliverable**: Production-ready application

### Phase 4: Enterprise (8-12 weeks, optional)
**Goal**: Enterprise features and scalability

- Migration to Dash or React
- Multi-user support with roles
- SSO integration (OAuth, SAML)
- Advanced caching (Redis)
- Horizontal scaling
- Audit logging
- Custom branding
- API rate limiting

**Deliverable**: Enterprise-grade platform

## File Structure

```
web_gui/
├── app.py                      # Main Streamlit app
├── requirements.txt            # Python dependencies
├── .streamlit/
│   ├── config.toml            # Streamlit configuration
│   └── secrets.toml           # API keys (gitignored)
├── pages/
│   ├── 01_📊_Dashboard.py
│   ├── 02_🔍_Market_Screening.py
│   ├── 03_📍_Market_Details.py
│   ├── 04_💼_Portfolio.py
│   ├── 05_📊_Reports.py
│   ├── 06_💾_Data_Management.py
│   └── 07_⚙️_Settings.py
├── components/
│   ├── __init__.py
│   ├── charts.py              # Plotly chart helpers
│   ├── maps.py                # Map components
│   ├── tables.py              # Table components
│   ├── filters.py             # Filter components
│   └── export.py              # Export utilities
├── utils/
│   ├── __init__.py
│   ├── state.py               # Session state management
│   ├── api.py                 # Backend API client
│   ├── auth.py                # Authentication
│   └── formatting.py          # Data formatting
├── assets/
│   ├── styles.css             # Custom CSS
│   ├── logo.png               # Aker logo
│   └── favicon.ico            # Browser icon
├── api/                        # FastAPI backend
│   ├── main.py                # API entry point
│   ├── endpoints/
│   │   ├── markets.py
│   │   ├── portfolio.py
│   │   ├── reports.py
│   │   └── cache.py
│   └── models.py              # Pydantic models
├── tests/
│   ├── test_components.py
│   ├── test_api.py
│   └── test_e2e.py
└── README.md
```

## Getting Started

### Installation

```bash
# Clone repository
git clone https://github.com/aker/platform.git
cd platform/web_gui

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Configure secrets
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit secrets.toml with your API keys
```

### Running Locally

```bash
# Start Streamlit app
streamlit run app.py

# Start backend API (separate terminal)
cd api
uvicorn main:app --reload

# Open browser to http://localhost:8501
```

### Deployment

```bash
# Deploy to Streamlit Cloud
# 1. Push to GitHub
# 2. Connect repository in Streamlit Cloud dashboard
# 3. Configure secrets in Streamlit Cloud
# 4. Deploy

# Deploy with Docker
docker-compose up -d

# Deploy to cloud (AWS, GCP, Azure)
# See deployment guide in docs/
```

## User Guide

### For Analysts

1. **Screen Markets**: Use filters to find markets matching criteria
2. **Analyze Details**: Deep-dive into individual market metrics
3. **Track Portfolio**: Add promising markets to portfolio
4. **Compare Options**: Side-by-side comparison of markets
5. **Generate Reports**: Create PDF reports for stakeholders

### For Managers

1. **Dashboard**: Monitor portfolio performance
2. **Portfolio Overview**: Track all active markets
3. **Reports**: Generate executive summaries
4. **Alerts**: Review market changes and new risks

### For Admins

1. **Settings**: Configure API keys and preferences
2. **Data Management**: Manage cache and data sources
3. **User Management**: Add/remove users (Phase 4)

## API Documentation

### Authentication

```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password"
}

Response:
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### Market Endpoints

```bash
# Screen markets
POST /api/markets/screen
Authorization: Bearer {token}
Content-Type: application/json

{
  "filters": {
    "supply_min": 60,
    "jobs_min": 50,
    "urban_min": 40
  }
}

# Get market details
GET /api/markets/{market_id}
Authorization: Bearer {token}
```

See full API documentation in `/docs` (FastAPI auto-generated)

## Support

- **Documentation**: See `docs/` directory
- **Issues**: GitHub Issues
- **Email**: support@aker-platform.com
- **Slack**: #aker-platform (internal)

## License

Proprietary - Aker Investment Platform
Copyright © 2024 Aker Capital Management
