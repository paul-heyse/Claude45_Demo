# Web GUI Design Document

## Architecture Overview

### Technology Stack Decision

**Selected: Streamlit for MVP, Dash/React for Production**

**Rationale:**

- **Streamlit**: Fastest path to MVP, Python-native, minimal frontend code
- **Dash/Plotly**: Production-ready, better performance, more customization
- **React Alternative**: Maximum flexibility, requires full-stack development

**Phase 1 (MVP):** Streamlit

- Quick prototyping (days vs. weeks)
- Python-native (no context switching)
- Built-in components (charts, tables, maps)
- Easy deployment (Streamlit Cloud, Docker)

**Phase 2 (Production):** Dash or React

- Better performance (async, caching)
- More control over UX
- Enterprise features (auth, SSO)
- Mobile-optimized

### Application Structure

```
web_gui/
├── app.py                    # Main Streamlit app
├── pages/                    # Multi-page structure
│   ├── 01_dashboard.py
│   ├── 02_market_screening.py
│   ├── 03_market_details.py
│   ├── 04_portfolio.py
│   ├── 05_reports.py
│   ├── 06_data_management.py
│   └── 07_settings.py
├── components/               # Reusable UI components
│   ├── charts.py
│   ├── maps.py
│   ├── tables.py
│   └── filters.py
├── utils/                    # Helper functions
│   ├── state.py             # Session state management
│   ├── api.py               # Backend API calls
│   └── export.py            # PDF/Excel generation
├── assets/                   # Static assets
│   ├── styles.css
│   ├── logo.png
│   └── favicon.ico
└── config/
    └── config.yaml          # App configuration
```

---

## Component Design

### Dashboard Page

**Layout:**

```
┌─────────────────────────────────────────────────────────┐
│ 📊 Dashboard                                 [Refresh]  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │Portfolio │  │Markets   │  │Cache Hit │  │  Data  │ │
│  │  $2.5M   │  │   24     │  │  87.3%   │  │Sources │ │
│  │  +12.4%  │  │  Active  │  │          │  │   12   │ │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘ │
│                                                          │
│  ┌────────────────────────┐  ┌──────────────────────┐  │
│  │ Portfolio Value        │  │ Top Markets          │  │
│  │ [Line Chart]           │  │ [Bar Chart]          │  │
│  │                        │  │                      │  │
│  └────────────────────────┘  └──────────────────────┘  │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Geographic Distribution [Interactive Map]        │   │
│  │                                                  │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  Quick Actions:                                          │
│  [Screen Markets] [Generate Report] [Warm Cache]        │
└─────────────────────────────────────────────────────────┘
```

**Key Components:**

- Metric cards (KPIs)
- Time-series charts (Plotly line/area)
- Bar charts (Plotly bar)
- Interactive map (Plotly mapbox or Folium)
- Action buttons (st.button)

**Data Flow:**

1. Load cached portfolio data from backend
2. Fetch recent statistics (last 7 days)
3. Render charts with cached data
4. Refresh button triggers API call + cache update

---

### Market Screening Page

**Layout:**

```
┌─────────────────────────────────────────────────────────┐
│ 🔍 Market Screening                                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Search: [___________________] [Screen] [Upload CSV]    │
│                                                          │
│  Filters:                                                │
│  Supply Constraint:  [━━━●━━━━━━] 60-100                │
│  Innovation Jobs:    [━━━━●━━━━] 50-100                 │
│  Urban Convenience:  [━━━●━━━━━━] 40-100                │
│  Risk Multiplier:    [━━━━━●━━━━] 0.7-1.3               │
│                                                          │
│  [Apply Filters] [Reset]                                │
│                                                          │
│  Results (127 markets):                                  │
│  ┌────────────────────────────────────────────────────┐ │
│  │Market     State Score Supply Jobs Urban Risk  [⚙]│ │
│  ├────────────────────────────────────────────────────┤ │
│  │Boulder    CO    87.2  95.1  82.3  78.9  0.92  [...│ │
│  │Fort C...  CO    84.5  89.7  85.2  75.1  0.95  [...│ │
│  │Denver     CO    82.1  78.3  88.9  89.2  1.05  [...│ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  [Export CSV] [Export Excel] [Export PDF]               │
└─────────────────────────────────────────────────────────┘
```

**Key Components:**

- Search bar with autocomplete
- Range sliders (st.slider)
- Data table (st.dataframe with AgGrid)
- Export buttons
- Pagination controls

**Implementation:**

```python
# Streamlit example
st.title("🔍 Market Screening")

# Search
search_term = st.text_input("Search markets", placeholder="Enter city or state...")

# Filters
st.subheader("Filters")
col1, col2 = st.columns(2)
with col1:
    supply_min = st.slider("Supply Constraint (min)", 0, 100, 60)
    jobs_min = st.slider("Innovation Jobs (min)", 0, 100, 50)
with col2:
    urban_min = st.slider("Urban Convenience (min)", 0, 100, 40)
    risk_max = st.slider("Risk Multiplier (max)", 0.7, 1.3, 1.2)

# Apply filters
if st.button("Apply Filters"):
    results = api.screen_markets(
        search=search_term,
        filters={
            "supply_min": supply_min,
            "jobs_min": jobs_min,
            "urban_min": urban_min,
            "risk_max": risk_max
        }
    )
    st.session_state.results = results

# Display results
if "results" in st.session_state:
    st.dataframe(st.session_state.results)
```

---

### Market Details Page

**Layout:**

```
┌─────────────────────────────────────────────────────────┐
│ 📍 Boulder, CO                           [Add to Port.] │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────┐                                    │
│  │  Composite Score │                                    │
│  │      87.2        │  Excellent market for investment  │
│  │  [█████████░]    │  Top 10% nationwide               │
│  └─────────────────┘                                    │
│                                                          │
│  Score Breakdown:              Risk Assessment:          │
│  ┌──────────────────────┐     ┌─────────────────────┐  │
│  │  [Radar Chart]       │     │ Risk Multiplier: 0.92│  │
│  │  Supply: 95.1        │     │ [Gauge Chart]        │  │
│  │  Jobs: 82.3          │     │ Wildfire: Low        │  │
│  │  Urban: 78.9         │     │ Flood: Moderate      │  │
│  │  Outdoor: 91.5       │     │ Seismic: Low         │  │
│  └──────────────────────┘     └─────────────────────┘  │
│                                                          │
│  Interactive Map:                                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │ [Mapbox/Folium]                                  │   │
│  │ • Market boundary                                │   │
│  │ • POIs (restaurants, parks, transit)            │   │
│  │ • Risk zones (flood plains, fire zones)        │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  Historical Trends:                                      │
│  [Tab: Employment] [Tab: Permits] [Tab: Population]     │
│  ┌─────────────────────────────────────────────────┐   │
│  │ [Line Chart: Last 5 years]                       │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  Data Sources:                                           │
│  Census ACS (2022), BLS QCEW (Q4 2023), OSM (current)   │
└─────────────────────────────────────────────────────────┘
```

**Key Components:**

- Large score display (custom HTML/CSS)
- Radar chart (Plotly)
- Gauge chart (Plotly indicator)
- Interactive map (Mapbox or Folium)
- Tabs for historical data
- Line charts for trends

---

### Portfolio Management Page

**Layout:**

```
┌─────────────────────────────────────────────────────────┐
│ 💼 Portfolio                        [Add Market] [⚙]    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Summary:                                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ 24 Markets│  │Avg Score │  │Portfolio │             │
│  │  Tracked  │  │  83.5    │  │Risk: Low │             │
│  └──────────┘  └──────────┘  └──────────┘             │
│                                                          │
│  Markets:                                                │
│  ┌────────────────────────────────────────────────────┐ │
│  │[x] Market  State Added   Score Δ  Status    [⚙]   │ │
│  ├────────────────────────────────────────────────────┤ │
│  │[x] Boulder CO  2024-01  87.2 +2.1 Prospect  [...] │ │
│  │[ ] Denver  CO  2024-02  82.1 -1.5 Active    [...] │ │
│  │[x] SLC     UT  2024-02  85.7 +0.8 Committed [...] │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  Selected (2):  [Compare] [Export] [Remove]             │
│                                                          │
│  Portfolio Performance:                                  │
│  ┌─────────────────────────────────────────────────┐   │
│  │ [Area Chart: Portfolio value over time]         │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

**Key Features:**

- Editable table with checkboxes
- Inline notes editing
- Bulk actions (compare, export, remove)
- Portfolio-level charts
- Alert notifications

---

## State Management

### Session State Schema

```python
# Streamlit session state structure
st.session_state = {
    # User session
    "user_id": str,
    "logged_in": bool,
    "api_token": str,

    # Application state
    "current_page": str,
    "last_refresh": datetime,

    # Data cache
    "portfolio": List[Dict],
    "screening_results": List[Dict],
    "selected_market": Dict,
    "cache_stats": Dict,

    # UI state
    "filters": Dict,
    "sort_by": str,
    "page_number": int,
    "selected_markets": List[str],

    # Settings
    "theme": str,  # "light", "dark"
    "map_style": str,
    "results_per_page": int,
}
```

### State Persistence

**Browser Storage:**

- Use `st.session_state` for current session
- Persist to localStorage for cross-session
- Clear sensitive data (API tokens) on logout

**Backend Sync:**

- Sync portfolio changes to backend immediately
- Lazy load data on page navigation
- Implement optimistic updates for responsiveness

---

## Styling and Theming

### Custom CSS

```css
/* assets/styles.css */

:root {
    --primary-color: #1E40AF;
    --secondary-color: #059669;
    --warning-color: #D97706;
    --danger-color: #DC2626;
    --text-color: #1F2937;
    --bg-color: #F9FAFB;
    --border-color: #E5E7EB;
}

/* Score color gradient */
.score-excellent { color: #059669; }
.score-good { color: #2563EB; }
.score-fair { color: #D97706; }
.score-poor { color: #DC2626; }

/* Card styling */
.metric-card {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

/* Data table */
.dataframe {
    font-family: 'Inter', sans-serif;
    font-size: 14px;
}

/* Responsive breakpoints */
@media (max-width: 768px) {
    .metric-card {
        padding: 15px;
    }
}
```

### Streamlit Theme Configuration

```toml
# .streamlit/config.toml
[theme]
primaryColor = "#1E40AF"
backgroundColor = "#F9FAFB"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#1F2937"
font = "sans serif"

[server]
maxUploadSize = 200
enableCORS = false
```

---

## API Integration

### Backend API Client

```python
# utils/api.py
import requests
from typing import Dict, List, Optional

class AkerAPIClient:
    def __init__(self, base_url: str, api_token: Optional[str] = None):
        self.base_url = base_url
        self.api_token = api_token
        self.session = requests.Session()
        if api_token:
            self.session.headers["Authorization"] = f"Bearer {api_token}"

    def screen_markets(self, filters: Dict) -> List[Dict]:
        """Screen markets with filters."""
        response = self.session.post(
            f"{self.base_url}/api/markets/screen",
            json=filters
        )
        response.raise_for_status()
        return response.json()

    def get_market_details(self, market_id: str) -> Dict:
        """Get detailed market information."""
        response = self.session.get(
            f"{self.base_url}/api/markets/{market_id}"
        )
        response.raise_for_status()
        return response.json()

    def get_portfolio(self) -> List[Dict]:
        """Get user's portfolio markets."""
        response = self.session.get(
            f"{self.base_url}/api/portfolio"
        )
        response.raise_for_status()
        return response.json()

    def add_to_portfolio(self, market_id: str, notes: str = "") -> Dict:
        """Add market to portfolio."""
        response = self.session.post(
            f"{self.base_url}/api/portfolio",
            json={"market_id": market_id, "notes": notes}
        )
        response.raise_for_status()
        return response.json()

    def generate_report(self, market_ids: List[str], template: str) -> bytes:
        """Generate PDF report."""
        response = self.session.post(
            f"{self.base_url}/api/reports/generate",
            json={"market_ids": market_ids, "template": template}
        )
        response.raise_for_status()
        return response.content

    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        response = self.session.get(
            f"{self.base_url}/api/cache/stats"
        )
        response.raise_for_status()
        return response.json()
```

---

## Performance Optimization

### Caching Strategy

**Streamlit Caching:**

```python
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_portfolio():
    """Load portfolio data with caching."""
    return api.get_portfolio()

@st.cache_resource
def get_api_client():
    """Singleton API client instance."""
    return AkerAPIClient(
        base_url=st.secrets["API_BASE_URL"],
        api_token=st.secrets.get("API_TOKEN")
    )
```

**Lazy Loading:**

- Load only visible data (first 50 results)
- Infinite scroll for large tables
- Defer non-critical charts until scroll

**Progressive Enhancement:**

- Render static content first
- Load interactive charts asynchronously
- Display skeleton screens during load

---

## Deployment

### Streamlit Cloud

```bash
# Deploy to Streamlit Cloud
# 1. Push to GitHub
# 2. Connect repo in Streamlit Cloud
# 3. Configure secrets in Streamlit dashboard
# 4. Deploy

# Requirements: .streamlit/secrets.toml (local), Streamlit Cloud secrets (production)
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8501:8501"
    environment:
      - API_BASE_URL=http://api:8000
    volumes:
      - ./config:/app/config

  api:
    image: aker-platform-api:latest
    ports:
      - "8000:8000"
```

---

## Security Considerations

### Authentication

**Phase 1 (MVP):** Basic authentication

- Environment variable for master password
- Single-user mode

**Phase 2 (Production):** OAuth/SSO

- Integration with Auth0, Okta, or Azure AD
- Role-based access control (Admin, Analyst, Viewer)
- Session management with JWT tokens

### Data Protection

- HTTPS only (enforce SSL)
- Secure cookie flags (httpOnly, secure, sameSite)
- API token encryption in browser storage
- Input sanitization (prevent XSS)
- Rate limiting on backend

---

## Testing Strategy

### Unit Tests

```python
# tests/test_components.py
def test_score_color_mapping():
    assert get_score_color(90) == "excellent"
    assert get_score_color(70) == "good"
    assert get_score_color(50) == "fair"
    assert get_score_color(30) == "poor"
```

### Integration Tests

- Test API client with mock backend
- Test state management across pages
- Test export functionality (PDF, Excel, CSV)

### End-to-End Tests

- Use Selenium or Playwright
- Test full user workflows:
  1. Login → Search → View Details → Add to Portfolio
  2. Portfolio → Compare → Generate Report
  3. Settings → Configure API → Test Connection

### Accessibility Testing

- WAVE (Web Accessibility Evaluation Tool)
- axe DevTools
- Keyboard navigation testing
- Screen reader testing (NVDA, JAWS)

---

## Migration Path

### MVP → Production

**Streamlit → Dash:**

1. Refactor page structure (similar layout)
2. Convert st.components to Dash components
3. Implement callback system
4. Add async data loading
5. Enhance mobile experience

**Dash → React:**

1. Create REST API backend (FastAPI)
2. Build React frontend (Next.js)
3. Implement Redux for state management
4. Use Recharts/Plotly.js for visualizations
5. Add PWA capabilities

**Timeline:**

- MVP (Streamlit): 2-3 weeks
- Production (Dash): 4-6 weeks
- Enterprise (React): 8-12 weeks
