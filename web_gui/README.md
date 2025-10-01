# Aker Investment Platform - Web GUI

Multi-page Streamlit application for real estate investment analysis and market screening.

## Quick Start

### Installation

```bash
# Navigate to web_gui directory
cd web_gui

# Install dependencies
pip install -r requirements.txt

# Copy secrets template
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Edit secrets.toml with your API keys
nano .streamlit/secrets.toml
```

### Running Locally

```bash
# Start Streamlit app
streamlit run app.py

# App will open at http://localhost:8501
```

### Demo Login

- Username: `demo@aker.com`
- Password: `demo`

## Project Structure

```
web_gui/
├── app.py                      # Main application entry point
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .streamlit/
│   ├── config.toml            # Streamlit configuration
│   └── secrets.toml.example   # Secrets template
├── assets/
│   └── styles.css             # Custom CSS
├── components/
│   ├── charts.py              # Chart components
│   ├── maps.py                # Map components
│   ├── tables.py              # Table components
│   └── filters.py             # Filter components
├── pages/
│   ├── 01_📊_Dashboard.py
│   ├── 02_🔍_Market_Screening.py
│   ├── 03_📍_Market_Details.py
│   ├── 04_💼_Portfolio.py
│   ├── 05_📊_Reports.py
│   ├── 06_💾_Data_Management.py
│   └── 07_⚙️_Settings.py
├── utils/
│   ├── __init__.py
│   ├── state.py               # Session state management
│   ├── api.py                 # Backend API client
│   ├── auth.py                # Authentication
│   └── formatting.py          # Data formatting
├── api/                        # FastAPI backend (future)
│   ├── main.py
│   └── endpoints/
└── tests/
    ├── test_components.py
    └── test_utils.py
```

## Features

- 📊 **Dashboard**: Portfolio overview, performance metrics, geographic distribution
- 🔍 **Market Screening**: Search, filter, and screen markets
- 📍 **Market Details**: Comprehensive market analysis with charts and maps
- 💼 **Portfolio**: Track and manage investment prospects
- 📊 **Reports**: Generate PDF/Excel reports
- 💾 **Data Management**: Cache inspection and data source management
- ⚙️ **Settings**: API configuration and preferences

## Development

### Adding a New Page

1. Create file in `pages/` directory with naming format: `NN_🔤_Page_Name.py`
2. Import utilities: `from utils import get_api_client, check_auth, format_score`
3. Add page content using Streamlit components
4. Update navigation in `app.py` if needed

### Styling

- Edit `assets/styles.css` for custom styles
- Use CSS classes: `.score-excellent`, `.score-good`, `.score-fair`, `.score-poor`
- Configure theme in `.streamlit/config.toml`

### API Integration

```python
from utils import get_api_client

# Get API client
api = get_api_client()

# Screen markets
results = api.screen_markets(
    search="Boulder",
    filters={"supply_min": 60}
)

# Get market details
details = api.get_market_details("boulder-co")
```

## Deployment

### Streamlit Cloud

1. Push repository to GitHub
2. Connect to Streamlit Cloud
3. Configure secrets in Streamlit dashboard
4. Deploy

### Docker

```bash
# Build image
docker build -t aker-platform-web .

# Run container
docker run -p 8501:8501 aker-platform-web
```

### Production

See `docs/deployment.md` for production deployment guide.

## Configuration

### Environment Variables

```bash
API_BASE_URL=http://localhost:8000
API_TIMEOUT=30
```

### Secrets (.streamlit/secrets.toml)

```toml
[api]
base_url = "http://localhost:8000"
timeout = 30

[api_keys]
census = "YOUR_KEY"
bls = "YOUR_KEY"

[auth]
secret_key = "YOUR_SECRET"
```

## Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=utils --cov=components tests/
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8501
lsof -i :8501

# Kill process
kill -9 <PID>
```

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Secrets Not Loading

- Ensure `.streamlit/secrets.toml` exists
- Check file permissions
- Restart Streamlit

## Support

- **Documentation**: See `docs/` directory
- **Issues**: GitHub Issues
- **Email**: <support@aker-platform.com>

## License

Proprietary - Aker Investment Platform
Copyright © 2024 Aker Capital Management
