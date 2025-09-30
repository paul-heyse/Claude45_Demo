#!/bin/bash
# Development environment setup script
# Run this after cloning the repository

set -e  # Exit on error

echo "🚀 Setting up Aker Investment Platform development environment..."

# Check if micromamba is available
if ! command -v micromamba &> /dev/null; then
    echo "❌ micromamba not found. Please install micromamba first."
    exit 1
fi

# Activate environment
echo "📦 Activating micromamba environment..."
eval "$(micromamba shell hook --shell bash)"
micromamba activate ./.venv || {
    echo "❌ Could not activate .venv. Creating new environment..."
    micromamba create -p ./.venv python=3.11 -y
    micromamba activate ./.venv
}

# Install core dependencies
echo "📚 Installing core dependencies..."
micromamba install -p ./.venv -c conda-forge \
    pandas \
    numpy \
    geopandas \
    shapely \
    scikit-learn \
    requests \
    matplotlib \
    seaborn \
    pyyaml \
    python-dotenv \
    -y

# Install development dependencies
echo "🔧 Installing development dependencies..."
micromamba install -p ./.venv -c conda-forge \
    pytest \
    pytest-cov \
    pytest-mock \
    ruff \
    black \
    mypy \
    ipython \
    jupyter \
    -y

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p .cache
mkdir -p logs
mkdir -p data/raw
mkdir -p data/processed
mkdir -p outputs/reports
mkdir -p outputs/figures
mkdir -p tests/fixtures

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env template..."
    cat > .env << 'EOF'
# API Keys (DO NOT COMMIT THIS FILE)
CENSUS_API_KEY=your_key_here
BLS_API_KEY=your_key_here
EPA_API_KEY=
GOOGLE_PLACES_API_KEY=

# Optional: override cache location
CACHE_DB_PATH=.cache/aker_platform.db

# Optional: logging level
LOG_LEVEL=INFO
EOF
    echo "✅ Created .env template. Please add your API keys."
else
    echo "✅ .env file already exists"
fi

# Create .gitignore additions
echo "🔒 Updating .gitignore..."
cat >> .gitignore << 'EOF'

# Aker Platform specific
.cache/
logs/
data/raw/
data/processed/
outputs/
*.db
*.db-journal
.env

# Jupyter
.ipynb_checkpoints/
*.ipynb
EOF

# Initialize OpenSpec if not already done
if [ ! -d "openspec/specs" ]; then
    echo "📋 Initializing OpenSpec..."
    openspec init . || echo "⚠️  OpenSpec init failed (may already be initialized)"
fi

# Run initial tests to verify setup
echo "🧪 Running initial tests..."
pytest tests/test_basic.py -v || echo "⚠️  Some tests failed (expected for new setup)"

# Validate OpenSpec
echo "✅ Validating OpenSpec proposal..."
openspec validate add-aker-investment-platform --strict

echo ""
echo "✨ Setup complete! Next steps:"
echo ""
echo "1. Add API keys to .env file:"
echo "   - Census API: https://api.census.gov/data/key_signup.html"
echo "   - BLS API: https://www.bls.gov/developers/api_signature_v2.shtml"
echo ""
echo "2. Review the OpenSpec proposal:"
echo "   openspec show add-aker-investment-platform"
echo ""
echo "3. Start development by reading:"
echo "   - .agentic/CONTEXT.md (project context)"
echo "   - .agentic/EXAMPLES.md (code examples)"
echo "   - openspec/changes/add-aker-investment-platform/tasks.md"
echo ""
echo "4. Activate environment and start coding:"
echo "   micromamba activate ./.venv"
echo "   pytest  # Run tests"
echo "   ruff check src  # Lint"
echo "   black src  # Format"
echo ""
echo "Happy coding! 🎉"

