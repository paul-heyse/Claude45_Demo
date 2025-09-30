# Module 8: CLI & Reporting - Implementation Guide

## Overview

Module 8 provides the user-facing interface for the Aker Investment Platform, enabling users to run market analyses, generate reports, and manage data through a command-line interface (CLI). This module makes all the underlying capabilities (Modules 1-7) accessible to end users.

## Architecture

```
aker-platform
├── screen           # Bulk market screening
├── analyze          # Single-property diligence
├── report           # Generate reports
├── data             # Data management
├── config           # Configuration management
└── validate         # Validation utilities
```

## Module Dependencies

Module 8 integrates and exposes:

- **Module 1** (Data Integration) - API connectors and caching
- **Module 2** (Geographic Analysis) - Geospatial calculations
- **Module 3** (Market Analysis) - Market scoring
- **Module 4** (Risk Assessment) - Risk modeling
- **Module 5** (Scoring Engine) - Weighted scoring
- **Module 6** (Asset Evaluation) - Deal filtering
- **Module 7** (State-Specific Rules) - CO/UT/ID logic

## Task Breakdown

### 8.1: Build CLI Entry Point ⏳

**Status:** In Progress
**Priority:** P0 (Foundation)
**Dependencies:** None
**Estimated Effort:** 4-6 hours

Create the main CLI application using `click` framework with:

- Command group structure (`aker-platform <command> <subcommand>`)
- Global options (--verbose, --config, --cache-dir)
- Help text and usage examples
- Version information

**Files to Create:**

- `src/Claude45_Demo/cli/__init__.py`
- `src/Claude45_Demo/cli/main.py`
- `setup.py` or `pyproject.toml` entry point

### 8.2: Implement Market Screening Command

**Status:** Not Started
**Priority:** P0 (Core Feature)
**Dependencies:** 8.1
**Estimated Effort:** 8-12 hours

Bulk analysis command that:

- Accepts CSV of submarkets (name, lat, lon, state)
- Runs full analysis pipeline (market, geo, risk, scoring)
- Outputs ranked results
- Supports parallel processing
- Shows progress indicators

**Command:** `aker-platform screen --input markets.csv --output results/`

### 8.3: Create Single-Property Diligence Command

**Status:** Not Started
**Priority:** P1 (Core Feature)
**Dependencies:** 8.1
**Estimated Effort:** 6-8 hours

Deep-dive analysis command that:

- Analyzes a single property address
- Generates comprehensive report
- Includes all risk factors
- Provides deal-specific recommendations
- Exports detailed JSON/PDF

**Command:** `aker-platform analyze --address "123 Main St, Boulder, CO" --report-type pdf`

### 8.4: Build Report Generation

**Status:** Not Started
**Priority:** P0 (Core Feature)
**Dependencies:** 8.1
**Estimated Effort:** 12-16 hours

Report generation supporting:

- **PDF Reports** - Professional investment memos
- **HTML Reports** - Interactive dashboards
- **CSV Exports** - Data for Excel analysis
- **JSON Output** - Machine-readable results

**Templates:**

- Executive summary
- Market analysis deep-dive
- Risk assessment report
- Comparative analysis

### 8.5: Implement Data Refresh Commands

**Status:** Not Started
**Priority:** P1 (Maintenance)
**Dependencies:** 8.1
**Estimated Effort:** 4-6 hours

Data management commands:

- `aker-platform data refresh` - Update cache
- `aker-platform data clear --older-than 30d` - Clear stale cache
- `aker-platform data status` - Show cache statistics
- `aker-platform data sources` - List available data sources

### 8.6: Create Configuration Wizard

**Status:** Not Started
**Priority:** P1 (User Experience)
**Dependencies:** 8.1
**Estimated Effort:** 6-8 hours

Interactive setup wizard:

- API key configuration
- Default scoring weights
- State selection (CO/UT/ID)
- Cache settings
- Output preferences

**Command:** `aker-platform config init`

### 8.7: Build Progress Indicators

**Status:** Not Started
**Priority:** P2 (Polish)
**Dependencies:** 8.2, 8.3
**Estimated Effort:** 4-6 hours

User feedback during long operations:

- Progress bars (using `tqdm` or `rich`)
- Status messages
- Time estimates
- Error notifications
- Success confirmations

### 8.8: Write CLI Integration Tests

**Status:** Not Started
**Priority:** P0 (Quality)
**Dependencies:** 8.1-8.7
**Estimated Effort:** 8-10 hours

Test suite covering:

- Command parsing
- Input validation
- Error handling
- Output formats
- Edge cases

### 8.9: Create User Documentation

**Status:** Not Started
**Priority:** P1 (Documentation)
**Dependencies:** 8.1-8.7
**Estimated Effort:** 8-12 hours

Documentation including:

- Quickstart guide
- Command reference
- Configuration guide
- Common workflows
- Troubleshooting

### 8.10: Build Sample Datasets

**Status:** Not Started
**Priority:** P2 (Demos)
**Dependencies:** None
**Estimated Effort:** 4-6 hours

Example data for demonstrations:

- Sample market CSV (10-20 markets)
- Known good/bad examples
- Tutorial datasets
- Benchmark markets

## CLI Design Principles

### 1. **Intuitive Command Structure**

```bash
aker-platform <verb> [options]
```

Examples:

- `aker-platform screen --input markets.csv`
- `aker-platform analyze --address "123 Main St"`
- `aker-platform report --market Boulder --format pdf`

### 2. **Sensible Defaults**

- Use cached data by default
- Output to `./output/` directory
- JSON format for machine consumption
- Human-readable for terminal output

### 3. **Explicit Configuration**

```bash
# Config file at ~/.aker-platform/config.yaml
aker-platform config set census_api_key ABC123
aker-platform config get cache_ttl_days
```

### 4. **Rich Feedback**

```
🔍 Screening 25 markets...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:32

✓ Analysis complete!
📊 Results saved to output/market-screening-2024-01-15.csv
🏆 Top market: Boulder, CO (Score: 87.3)
```

### 5. **Error Handling**

```bash
❌ Error: Census API key not configured
💡 Run: aker-platform config set census_api_key <your-key>
📖 Get a key: https://api.census.gov/data/key_signup.html
```

## Key Technical Decisions

### CLI Framework: Click

**Decision:** Use `click` instead of `argparse`

**Rationale:**

- More Pythonic API
- Better help text generation
- Composable command groups
- Type validation built-in
- Industry standard for modern Python CLIs

**Example:**

```python
import click

@click.group()
@click.version_option()
@click.option('--verbose', is_flag=True)
def cli(verbose):
    """Aker Investment Platform - Real Estate Analysis Tool"""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
```

### Progress Indicators: Rich

**Decision:** Use `rich` library for terminal UI

**Rationale:**

- Beautiful progress bars
- Syntax highlighting
- Tables and formatting
- Spinner animations
- Cross-platform support

### Report Generation: Libraries

- **PDF:** ReportLab or WeasyPrint (HTML → PDF)
- **HTML:** Jinja2 templates
- **CSV:** Built-in `csv` module + pandas
- **JSON:** Built-in `json` module

### Configuration: YAML

**Decision:** Use YAML for config files

**Location:** `~/.aker-platform/config.yaml`

**Example:**

```yaml
api_keys:
  census: ABC123
  bls: DEF456

scoring_weights:
  supply_constraint: 0.30
  innovation_employment: 0.30
  urban_convenience: 0.20
  outdoor_access: 0.20

cache:
  directory: ~/.aker-platform/cache
  ttl_days: 30

output:
  directory: ./output
  default_format: json
```

## Usage Examples

### Example 1: Bulk Market Screening

```bash
# Screen 50 markets from CSV
aker-platform screen \
  --input markets.csv \
  --output results/ \
  --format csv \
  --parallel 4

# Output: results/market-screening-2024-01-15.csv
```

### Example 2: Single Property Analysis

```bash
# Detailed analysis of one property
aker-platform analyze \
  --address "123 Main St, Boulder, CO" \
  --report pdf \
  --output diligence/boulder-main-st.pdf

# Interactive mode
aker-platform analyze --interactive
```

### Example 3: Generate Custom Report

```bash
# Create PDF investment memo
aker-platform report \
  --market "Boulder, CO" \
  --template investment-memo \
  --format pdf \
  --output reports/boulder-memo.pdf
```

### Example 4: Data Management

```bash
# Refresh all cached data
aker-platform data refresh --all

# Clear stale cache entries
aker-platform data clear --older-than 30d

# Show cache status
aker-platform data status
```

### Example 5: Configuration

```bash
# First-time setup wizard
aker-platform config init

# Set specific values
aker-platform config set census_api_key ABC123
aker-platform config set cache_ttl_days 45

# View current config
aker-platform config show
```

## Integration Points

### With Module 3 (Market Analysis)

```python
from Claude45_Demo.market_analysis import (
    SupplyConstraintCalculator,
    EmploymentAnalyzer,
    DemographicAnalyzer,
)

# CLI orchestrates the analysis
supply_calc = SupplyConstraintCalculator()
employment = EmploymentAnalyzer()
# ... run analyses and aggregate results
```

### With Module 5 (Scoring Engine)

```python
from Claude45_Demo.scoring_engine import ScoringEngine

# Apply scoring to results
engine = ScoringEngine()
composite = engine.calculate_composite_score(component_scores)
risk_adjusted = engine.apply_risk_adjustment(composite, risk_multiplier)
```

### With Report Generator (Module 3)

```python
from Claude45_Demo.market_analysis.report import MarketAnalysisReport

# Generate reports
reporter = MarketAnalysisReport()
report = reporter.generate_report(submarket_name, ...)
markdown = reporter.export_to_markdown(report)
```

## Testing Strategy

### Unit Tests

- Command parsing
- Option validation
- Configuration management
- Output formatting

### Integration Tests

- Full command execution
- File I/O operations
- Error scenarios
- Multi-step workflows

### End-to-End Tests

- Real data processing
- Report generation
- Cache management
- Performance benchmarks

## Success Criteria

✅ **User can run full market screening in < 5 commands**
✅ **Help text is clear and actionable**
✅ **Error messages guide user to solutions**
✅ **Progress indicators show during long operations**
✅ **Reports are professional and actionable**
✅ **Configuration is straightforward**
✅ **Test coverage > 80%**

## Implementation Order

**Week 1 (Foundation):**

1. Task 8.1: CLI entry point ← START HERE
2. Task 8.6: Configuration wizard
3. Task 8.5: Data refresh commands

**Week 2 (Core Features):**
4. Task 8.2: Market screening command
5. Task 8.3: Single-property diligence
6. Task 8.7: Progress indicators

**Week 3 (Polish):**
7. Task 8.4: Report generation (PDF/HTML/CSV)
8. Task 8.8: CLI integration tests
9. Task 8.9: User documentation
10. Task 8.10: Sample datasets

**Total Estimated Effort:** 3 weeks for complete Module 8

## Next Steps for Collaborators

### To Get Started

1. Read this guide thoroughly
2. Review existing modules (1-5) to understand capabilities
3. Install dependencies: `pip install click rich jinja2 pyyaml`
4. Start with Task 8.1 (CLI entry point)
5. Reference `MODULE_8_GUIDE.md` for design patterns

### To Contribute

1. Pick an unstarted task (8.2-8.10)
2. Create feature branch: `cx/module8-task-X.Y`
3. Write tests first (TDD approach)
4. Implement following project conventions
5. Update this guide with learnings
6. Submit PR with thorough documentation

### Questions?

- Check existing module implementations for patterns
- Review `openspec/project.md` for conventions
- Ask in team channel for clarifications

---

**Module 8 Status:** 🚀 Ready for Implementation
**Next Task:** 8.1 - Build CLI Entry Point
**Owner:** TBD
**Target Completion:** Week 1
