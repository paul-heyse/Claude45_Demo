# Deployment Guide - Aker Investment Platform Web GUI

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Streamlit Cloud Deployment](#streamlit-cloud-deployment)
4. [Production Deployment](#production-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Troubleshooting](#troubleshooting)

---

## Local Development

### Prerequisites

- Python 3.12+
- pip or micromamba
- Git

### Installation

```bash
# Clone repository
git clone https://github.com/aker/platform.git
cd platform/web_gui

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy secrets template
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Edit secrets with your API keys
nano .streamlit/secrets.toml
```

### Running Locally

```bash
# Start Streamlit (Web GUI)
streamlit run app.py

# In a separate terminal, start FastAPI (Backend)
cd api
uvicorn main:app --reload --port 8000

# Access the application
# Web GUI: http://localhost:8501
# API Docs: http://localhost:8000/docs
```

---

## Docker Deployment

### Quick Start

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Custom Build

```bash
# Build Web GUI image
docker build -t aker-platform-web:latest .

# Build API image
docker build -t aker-platform-api:latest -f Dockerfile.api ..

# Run Web GUI
docker run -p 8501:8501 \
  -e API_BASE_URL=http://api:8000 \
  aker-platform-web:latest

# Run API
docker run -p 8000:8000 \
  -v $(pwd)/cache:/app/cache \
  aker-platform-api:latest
```

### Docker Compose Services

- **web**: Streamlit GUI (port 8501)
- **api**: FastAPI backend (port 8000)
- **redis** (optional): Distributed cache (port 6379)

### Environment Variables

```yaml
# Web GUI
API_BASE_URL=http://api:8000
PYTHONUNBUFFERED=1

# API
DATABASE_URL=sqlite:///./aker_platform.db
CACHE_REDIS_URL=redis://redis:6379/0
```

---

## Streamlit Cloud Deployment

### Prerequisites

- GitHub repository
- Streamlit Cloud account

### Steps

1. **Push to GitHub**

   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Connect to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your repository
   - Choose branch: `main`
   - Set main file: `web_gui/app.py`

3. **Configure Secrets**
   - In Streamlit Cloud dashboard, go to app settings
   - Add secrets from `.streamlit/secrets.toml`
   - Format:

     ```toml
     [api]
     base_url = "http://your-api-url.com"

     [api_keys]
     census = "YOUR_CENSUS_KEY"
     bls = "YOUR_BLS_KEY"
     ```

4. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Access your app at `https://your-app.streamlit.app`

### Streamlit Cloud Tips

- Free tier: 1 app, 1 GB RAM, 1 CPU
- Custom domains supported (paid plans)
- Automatic redeployment on git push
- Built-in SSL/HTTPS
- App sleeping after inactivity (free tier)

---

## Production Deployment

### Cloud Providers

#### AWS (EC2 + ECS)

```bash
# 1. Create EC2 instance
# - Instance type: t3.medium or larger
# - OS: Ubuntu 22.04 LTS
# - Security groups: Allow 8501, 8000, 22

# 2. SSH into instance
ssh -i your-key.pem ubuntu@your-ip

# 3. Install Docker
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo usermod -aG docker $USER

# 4. Clone and deploy
git clone https://github.com/aker/platform.git
cd platform/web_gui
docker-compose up -d

# 5. Configure nginx (reverse proxy)
sudo apt-get install nginx
# Configure /etc/nginx/sites-available/aker-platform
```

#### Google Cloud Platform (Cloud Run)

```bash
# 1. Install gcloud CLI
# 2. Build and push container
gcloud builds submit --tag gcr.io/PROJECT_ID/aker-platform-web

# 3. Deploy to Cloud Run
gcloud run deploy aker-platform-web \
  --image gcr.io/PROJECT_ID/aker-platform-web \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Azure (Container Instances)

```bash
# 1. Login to Azure
az login

# 2. Create resource group
az group create --name aker-platform --location eastus

# 3. Deploy container
az container create \
  --resource-group aker-platform \
  --name aker-web \
  --image aker-platform-web:latest \
  --dns-name-label aker-platform \
  --ports 8501
```

### HTTPS/SSL

#### Using Nginx as Reverse Proxy

```nginx
# /etc/nginx/sites-available/aker-platform
server {
    listen 80;
    server_name your-domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }

    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
}
```

#### Let's Encrypt SSL Certificate

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

---

## Environment Configuration

### Required Secrets (.streamlit/secrets.toml)

```toml
[api]
base_url = "http://localhost:8000"
timeout = 30

[api_keys]
census = "YOUR_CENSUS_API_KEY"
bls = "YOUR_BLS_API_KEY"
bea = "YOUR_BEA_API_KEY"

[auth]
secret_key = "GENERATE_RANDOM_SECRET_KEY"
algorithm = "HS256"
access_token_expire_minutes = 1440

[database]
url = "sqlite:///./aker_platform.db"

[cache]
redis_url = "redis://localhost:6379/0"
default_ttl = 3600
```

### Generate Secret Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Environment-Specific Configuration

**Development** (`.env.dev`)

```bash
DEBUG=True
LOG_LEVEL=DEBUG
API_BASE_URL=http://localhost:8000
```

**Production** (`.env.prod`)

```bash
DEBUG=False
LOG_LEVEL=INFO
API_BASE_URL=https://api.your-domain.com
```

---

## Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Find process using port 8501
lsof -i :8501

# Kill process
kill -9 <PID>
```

#### Module Not Found

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Verify installation
pip list | grep streamlit
```

#### Secrets Not Loading

```bash
# Check file exists
ls -la .streamlit/secrets.toml

# Check file permissions
chmod 600 .streamlit/secrets.toml

# Verify format (must be valid TOML)
python -c "import tomli; tomli.load(open('.streamlit/secrets.toml', 'rb'))"
```

#### Docker Container Fails

```bash
# Check logs
docker-compose logs web

# Rebuild without cache
docker-compose build --no-cache

# Enter container for debugging
docker-compose exec web /bin/bash
```

#### API Connection Errors

```bash
# Test API connectivity
curl http://localhost:8000/health

# Check API logs
docker-compose logs api

# Verify network
docker network ls
docker network inspect aker-network
```

### Performance Optimization

#### Enable Cache Warming

```bash
# Warm cache for portfolio markets
curl -X POST http://localhost:8000/api/cache/warm \
  -H "Content-Type: application/json" \
  -d '{"markets": ["Boulder, CO", "Denver, CO"], "sources": ["census", "bls"]}'
```

#### Monitor Resource Usage

```bash
# Docker stats
docker stats

# System resources
htop
df -h
free -h
```

### Logging

```bash
# Streamlit logs
tail -f logs/streamlit.log

# API logs
tail -f logs/api.log

# Docker logs
docker-compose logs -f --tail=100
```

---

## Health Checks

### Application Health

```bash
# Web GUI health
curl http://localhost:8501/_stcore/health

# API health
curl http://localhost:8000/health

# Full system check
curl http://localhost:8000/
```

### Monitoring

```bash
# Set up monitoring (Prometheus + Grafana)
docker-compose -f docker-compose.monitoring.yml up -d

# Access Grafana: http://localhost:3000
# Default credentials: admin/admin
```

---

## Backup and Restore

### Database Backup

```bash
# Backup SQLite database
cp cache/aker_cache.db backups/aker_cache_$(date +%Y%m%d).db

# Automated backup (cron)
0 2 * * * /path/to/backup-script.sh
```

### Cache Backup

```bash
# Export cache data
curl http://localhost:8000/api/cache/export > cache_backup.json

# Import cache data
curl -X POST http://localhost:8000/api/cache/import \
  -H "Content-Type: application/json" \
  -d @cache_backup.json
```

---

## Support

- **Documentation**: [docs.aker-platform.com](https://docs.aker-platform.com)
- **Issues**: [github.com/aker/platform/issues](https://github.com/aker/platform/issues)
- **Email**: <support@aker-platform.com>
