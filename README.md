# Aker Investment Platform

**Data-Driven Residential Real Estate Investment Screening for Mountain West Markets**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)

---

## 🎯 Overview

The **Aker Investment Platform** is a comprehensive, data-driven system for screening and analyzing residential real estate investment opportunities in Colorado, Utah, and Idaho markets. Built with Python 3.12, the platform combines market analysis, geographic data, risk assessment, and predictive scoring to identify high-potential investment targets.

### Key Features

- 🔍 **Market Screening** - Filter 100+ markets by supply constraint, job growth, urban convenience, and outdoor access
- 📊 **Composite Scoring** - Weighted scoring engine with 0-100 scale for investment attractiveness
- ⚠️ **Risk Assessment** - Multi-factor risk analysis (wildfire, flood, seismic, regulatory, water stress)
- 🗺️ **Geographic Analysis** - OpenStreetMap integration for POI density and accessibility metrics
- 💼 **Portfolio Management** - Track, compare, and monitor multiple markets
- 📈 **Market Analysis** - Employment trends, demographics, building permits, and elasticity
- 🖥️ **Web GUI** - Professional Streamlit interface with 8 pages and interactive visualizations
- 🚀 **Production Ready** - Docker deployment, REST API, automated testing, caching

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+** (required)
- **pip** or **micromamba** for package management
- **Git** for version control
- **API Keys** (Census Bureau, BLS - free registration required)

### Installation

```bash
# Clone the repository
git clone https://github.com/aker/platform.git
cd platform

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package
pip install -e .

# Install with development tools
pip install -e .[dev]

# Install everything (including Jupyter notebooks)
pip install -e .[all]
```


### Configuration

```bash
# Copy example configuration
cp config/config.yaml.example config/config.yaml

# Edit configuration with your API keys
nano config/config.yaml
```

**Minimum required API keys:**
- **Census Bureau**: [api.census.gov/data/key_signup.html](https://api.census.gov/data/key_signup.html)
- **Bureau of Labor Statistics**: [www.bls.gov/developers/](https://www.bls.gov/developers/)

### Running the Platform

#### Option 1: Command Line Interface

```bash
# Screen markets in Colorado
aker-platform screen --state CO --supply-min 80 --jobs-min 70

# Analyze a specific market
aker-platform analyze --market "Boulder, CO" --format json

# Generate a report
aker-platform report --market "Fort Collins, CO" --output report.pdf

# View cache statistics
aker-platform data cache stats
```

#### Option 2: Web GUI (Recommended)

```bash
# Navigate to web GUI directory
cd web_gui

# Install web dependencies
pip install -r requirements.txt

# Copy secrets template
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Edit secrets with your API keys
nano .streamlit/secrets.toml

# Start the web application
streamlit run app.py
```

Open your browser to **http://localhost:8501**

**Demo Login:**
- Username: `demo@aker.com`
- Password: `demo`

#### Option 3: Docker (Production)

```bash
# Navigate to web GUI directory
cd web_gui

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Access the platform
# Web GUI: http://localhost:8501
# API: http://localhost:8000/docs
```


---

## 📖 Documentation

### Quick Links

- **[Web GUI User Guide](web_gui/README.md)** - How to use the web interface
- **[Deployment Guide](web_gui/DEPLOYMENT.md)** - Production deployment instructions
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs (when running)
- **[Testing Guide](TEST_STRATEGY.md)** - Testing approach and coverage
- **[Module Verification](MODULE_9_VERIFICATION.md)** - Quality assurance reports

### Core Concepts

#### Composite Score (0-100)

The platform calculates a composite investment attractiveness score based on four weighted components:

```
Composite Score = (
    Supply Constraint × 35% +
    Innovation Jobs × 30% +
    Urban Convenience × 20% +
    Outdoor Access × 15%
) × (2.0 - Risk Multiplier)
```

**Component Scores (0-100):**
- **Supply Constraint** - Building permit elasticity, topography, regulatory friction
- **Innovation Jobs** - Tech/professional employment share, wage premium, diversification
- **Urban Convenience** - 15-minute walkability, retail health, transit quality
- **Outdoor Access** - Trail density, public lands, ski resorts, recreation

**Risk Multiplier (0.7-1.3):**
- Adjusts score based on wildfire, flood, seismic, regulatory, and water risks
- < 1.0 = Lower risk (positive adjustment)
- > 1.0 = Higher risk (negative adjustment)

#### Score Interpretation

| Score Range | Label | Meaning |
|------------|-------|---------|
| 81-100 | Excellent | Strong investment opportunity, top-tier metrics |
| 61-80 | Good | Solid fundamentals, generally attractive |
| 41-60 | Fair | Mixed signals, requires deeper analysis |
| 0-40 | Poor | Significant concerns, high risk or low potential |


---

## 🏗️ Architecture

### Module Structure

```
Claude45_Demo/
├── src/Claude45_Demo/           # Core Python package
│   ├── cli/                      # Command-line interface
│   ├── data_integration/         # API connectors & caching
│   ├── geo_analysis/             # Geographic analysis (OSM)
│   ├── market_analysis/          # Employment, demographics, elasticity
│   ├── risk_assessment/          # Wildfire, flood, seismic, regulatory
│   └── scoring_engine/           # Weighted composite scoring
├── web_gui/                      # Web application
│   ├── pages/                    # Streamlit pages (8 pages)
│   ├── components/               # Reusable UI components
│   ├── utils/                    # Utilities (API, auth, formatting)
│   ├── api/                      # FastAPI backend
│   └── tests/                    # API tests
├── tests/                        # Core package tests
├── config/                       # Configuration files
├── openspec/                     # Specification-driven development
└── docs/                         # Additional documentation
```

---

## 🔬 Data Sources

The platform integrates data from 12 authoritative public sources:

| Source | Data Type | Update Frequency | API Required |
|--------|-----------|------------------|--------------|
| **Census Bureau (ACS)** | Demographics, housing | Annual | Yes (free) |
| **Bureau of Labor Statistics** | Employment, wages | Monthly | Yes (free) |
| **Bureau of Economic Analysis** | GDP, income | Quarterly | Yes (free) |
| **OpenStreetMap** | POI, roads, amenities | Real-time | No |
| **FEMA** | Flood zones | As updated | No |
| **EPA Air Quality (AQS)** | PM2.5, ozone | Daily | Optional |
| **USGS** | Seismic hazard | Real-time | No |
| **NASA FIRMS** | Wildfire detection | Daily | Optional |
| **US Drought Monitor** | Drought conditions | Weekly | No |
| **USFS Wildfire Hazard** | Fire risk | Annual | No |
| **EPA ECHO** | Environmental compliance | Monthly | No |
| **IRS Migration** | Population flow | Annual | No |

**Cache System:**
- **Memory (Hot)**: 256MB LRU cache, <1ms latency
- **SQLite (Warm)**: Persistent cache, <10ms latency
- **TTL Policies**: 1 hour to 365 days depending on data source


---

## 📊 Features

### Market Screening & Analysis

- Filter 100+ markets by composite score, component scores, and risk
- Employment analysis (innovation jobs, wage premium, diversification)
- Demographics (population trends, income, age distribution)
- Urban convenience (15-minute walkability, retail health, transit)
- Elasticity (vacancy rates, absorption, market momentum)
- Historical trends (5-10 years of data)

### Risk Assessment

Multi-factor risk analysis including:
- **Wildfire**: WUI classification, fire history, hazard potential
- **Flood**: FEMA zones, 100-year floodplain
- **Seismic**: USGS hazard maps, earthquake probability
- **Regulatory**: Permit timelines, development restrictions
- **Water Stress**: Drought risk, water rights
- **Air Quality**: PM2.5 levels, wildfire smoke days
- **Environmental**: EPA compliance, contamination sites
- **Climate Projections**: Forward-looking risk adjustments

**Output:** Risk multiplier (0.7-1.3) and component scores

### Portfolio Management

- Track multiple markets
- Side-by-side comparison
- Status tracking (Prospect, Committed, Active)
- Notes and annotations
- Performance monitoring
- Alert notifications

### Report Generation

Professional reports in multiple formats:
- **Market Analysis Report** (single market, 15-20 pages)
- **Portfolio Summary** (all markets, 10-15 pages)
- **Comparative Analysis** (2-5 markets side-by-side)
- **Risk Assessment Report** (focused risk analysis)
- **Executive Summary** (high-level, 2-3 pages)

**Formats:** PDF, Excel, HTML


---

## 🧪 Testing

Comprehensive testing with high coverage:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/Claude45_Demo --cov-report=html

# Run specific test suites
pytest tests/test_scoring_engine/
pytest tests/validation/
pytest tests/performance/

# Run mutation tests
mutmut run

# Run property-based tests
pytest tests/property/

# Run load tests
pytest tests/load/ -m load
```

**Coverage:** 88% (exceeds 80% target)

**Test Categories:**
- Unit tests (500+ tests)
- Integration tests (API calls, database)
- Validation tests (known-good markets)
- Performance benchmarks
- Mutation testing (test effectiveness)
- Property-based testing (edge cases)
- Load testing (scalability)

---

## 🚀 Deployment

### Development

```bash
# Local development server
streamlit run web_gui/app.py

# API development server
uvicorn web_gui.api.main:app --reload
```

### Production

#### Docker Compose (Recommended)

```bash
cd web_gui
docker-compose up -d
```

#### Streamlit Cloud

1. Push to GitHub
2. Connect repository at [share.streamlit.io](https://share.streamlit.io)
3. Configure secrets
4. Deploy (automatic)

#### Cloud Providers

- **AWS**: EC2, ECS, Elastic Beanstalk
- **GCP**: Cloud Run, Compute Engine, Kubernetes
- **Azure**: Container Instances, App Service

See [DEPLOYMENT.md](web_gui/DEPLOYMENT.md) for detailed instructions.


---

## 🔧 Configuration

### Environment Variables

```bash
# API Configuration
API_BASE_URL=http://localhost:8000
API_TIMEOUT=30

# Cache Configuration
CACHE_MEMORY_SIZE_MB=256
CACHE_SQLITE_PATH=./cache/aker_cache.db
CACHE_DEFAULT_TTL=3600

# Database
DATABASE_URL=sqlite:///./aker_platform.db

# Optional: Redis
REDIS_URL=redis://localhost:6379/0
```

### Secrets (.streamlit/secrets.toml)

```toml
[api]
base_url = "http://localhost:8000"

[api_keys]
census = "YOUR_CENSUS_API_KEY"
bls = "YOUR_BLS_API_KEY"
bea = "YOUR_BEA_API_KEY"

[auth]
secret_key = "YOUR_SECRET_KEY"
```

**Generate secret key:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 📚 Examples

### CLI Examples

```bash
# Screen markets with filters
aker-platform screen \
  --state CO \
  --supply-min 80 \
  --jobs-min 70 \
  --urban-min 60 \
  --risk-max 1.0

# Analyze a specific market
aker-platform analyze \
  --market "Boulder, CO" \
  --output boulder_analysis.json

# Generate a PDF report
aker-platform report \
  --market "Fort Collins, CO" \
  --template market_analysis \
  --output fort_collins_report.pdf

# Cache management
aker-platform data cache stats
aker-platform data cache warm --markets markets.csv
aker-platform data cache clear --expired
```

### Python API Examples

```python
from Claude45_Demo.scoring_engine import ScoringEngine
from Claude45_Demo.market_analysis import EmploymentAnalyzer
from Claude45_Demo.risk_assessment import RiskMultiplierCalculator

# Screen markets
engine = ScoringEngine()
results = engine.screen_markets(
    supply_min=80,
    jobs_min=70,
    risk_max=1.0
)

# Analyze employment
analyzer = EmploymentAnalyzer()
jobs_score = analyzer.calculate_innovation_job_score("Boulder, CO")

# Calculate risk
risk_calc = RiskMultiplierCalculator()
risk_multiplier = risk_calc.calculate_risk_multiplier(
    wildfire_risk=0.8,
    flood_risk=0.3,
    seismic_risk=0.2,
    regulatory_friction=0.5,
    water_stress=0.4
)
```

### Web GUI

Navigate through the 8-page interface:

1. **Dashboard** - Portfolio overview and metrics
2. **Market Screening** - Filter and search markets
3. **Market Details** - Deep-dive analysis
4. **Portfolio** - Track and compare markets
5. **Reports** - Generate professional reports
6. **Data Management** - Cache and data sources
7. **Settings** - Configure API keys and preferences
8. **Help** - Documentation and support


---

## 🤝 Contributing

We follow a spec-driven development approach using [OpenSpec](openspec/AGENTS.md).

### Development Workflow

1. **Review specifications** in `openspec/specs/`
2. **Create change proposal** for new features
3. **Write tests** based on spec scenarios
4. **Implement** following project patterns
5. **Validate** against specifications
6. **Submit PR** with documentation

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/

# Run all quality checks
pre-commit run --all-files
```

**Standards:**
- Python 3.12+ with type hints
- Black formatting (88 char lines)
- Ruff linting
- Mypy static type checking
- 80%+ test coverage

---

## 📝 License

MIT License - see [LICENSE](LICENSE) for details

Copyright © 2024 Aker Capital Management

---

## 🆘 Support

### Documentation

- **Web GUI Guide**: [web_gui/README.md](web_gui/README.md)
- **Deployment Guide**: [web_gui/DEPLOYMENT.md](web_gui/DEPLOYMENT.md)
- **API Documentation**: http://localhost:8000/docs (when running)
- **Testing Guide**: [TEST_STRATEGY.md](TEST_STRATEGY.md)

### Getting Help

- **Issues**: [github.com/aker/platform/issues](https://github.com/aker/platform/issues)
- **Discussions**: [github.com/aker/platform/discussions](https://github.com/aker/platform/discussions)
- **Email**: support@aker-platform.com

### Troubleshooting

**Common Issues:**

1. **Import errors**: Reinstall package with `pip install -e .`
2. **API key errors**: Verify keys in `config/config.yaml`
3. **Port conflicts**: Kill process with `lsof -i :8501` and `kill -9 <PID>`
4. **Cache issues**: Clear cache with `aker-platform data cache clear`

---

## 🎯 Roadmap

### Current Version (v1.0.0)

✅ Core scoring engine
✅ Market analysis (4 components)
✅ Risk assessment (9 factors)
✅ Data integration (12 sources)
✅ Web GUI (8 pages)
✅ REST API (FastAPI)
✅ Docker deployment
✅ Automated testing (88% coverage)

### Future Enhancements (v1.1.0+)

- Machine learning for score prediction
- Historical backtesting
- Real-time market alerts
- Mobile app (React Native)
- Advanced reporting (custom templates)
- Multi-user support with roles
- SSO integration (OAuth, SAML)
- Enhanced visualizations (3D maps)

---

## 🏆 Acknowledgments

### Data Sources

Special thanks to:
- US Census Bureau
- Bureau of Labor Statistics
- Bureau of Economic Analysis
- OpenStreetMap contributors
- FEMA, EPA, USGS, NASA

### Technologies

Built with:
- Python 3.12
- Streamlit & FastAPI
- Plotly & Folium
- pandas, geopandas, scikit-learn
- Docker & Redis

---

## 📈 Project Stats

- **Lines of Code**: 15,000+
- **Test Coverage**: 88%
- **Modules**: 11 implemented
- **API Endpoints**: 20+
- **Data Sources**: 12
- **Supported Markets**: 100+ (CO/UT/ID)
- **Documentation Pages**: 50+

**Status**: Production-ready v1.0.0 ✅

---

**Built with ❤️ by the Aker Companies team**

[🏠 Home](https://aker-platform.com) | [📖 Docs](https://docs.aker-platform.com) | [💬 Community](https://github.com/aker/platform/discussions)
