# End-to-End (E2E) Functional Tests

## Purpose

These tests verify complete user workflows from start to finish, ensuring all modules work together correctly for real-world usage in a **single-user environment**.

## Philosophy

The Aker Investment Platform is designed for **individual analysts** or small teams with **low concurrency** (typically 1 user at a time). Therefore, our E2E tests focus on:

✅ **Functional correctness** - Does the complete workflow work?
✅ **Data accuracy** - Are the results reasonable and validated?
✅ **Error handling** - Does the system gracefully handle failures?
✅ **User experience** - Can a user complete their task end-to-end?

❌ **NOT focused on:**

- Load testing (10+ concurrent users)
- Stress testing (finding breaking points)
- Performance under heavy load
- Scalability to thousands of users

## Test Structure

### Module 13: End-to-End Functional Testing

| Test File | Workflow | Real Markets Tested |
|-----------|----------|-------------------|
| `test_market_screening_e2e.py` | Complete market screening | Boulder, CO |
| `test_market_analysis_e2e.py` | Full analysis workflow | Fort Collins, CO |
| `test_portfolio_e2e.py` | Portfolio management | Boulder, Fort Collins, Boise |
| `test_cache_workflow_e2e.py` | Cache operations | N/A (synthetic data) |

### Module 14: Essential Quality & Security

| Aspect | Focus |
|--------|-------|
| API Key Validation | All 11 connectors reject invalid keys |
| Input Validation | Invalid FIPS, coordinates, dates |
| Credential Security | Keys not logged or exposed |
| Data Accuracy | Spot-check 10 markets |
| Boundary Conditions | Edge cases, empty results |

### Module 15: Simplified CI/CD

| Component | Schedule |
|-----------|----------|
| Unit Tests | Every commit (GitHub Actions) |
| E2E Tests | Weekly (scheduled) |
| Real API Tests | Monthly (live credentials) |
| Security Scan | Monthly (Bandit, Safety) |

## Running E2E Tests

### Run All E2E Tests

```bash
pytest tests/e2e/ -v
```

### Run Specific Workflow

```bash
# Market screening
pytest tests/e2e/test_market_screening_e2e.py -v

# Full analysis
pytest tests/e2e/test_market_analysis_e2e.py -v

# Portfolio
pytest tests/e2e/test_portfolio_e2e.py -v

# Cache
pytest tests/e2e/test_cache_workflow_e2e.py -v
```

### Run with Verbose Output

```bash
pytest tests/e2e/ -v -s
```

The `-s` flag shows print statements, which is useful for seeing the
workflow progress.

### Run with Real API Credentials

```bash
# Set API keys first
export CENSUS_API_KEY=your_key
export BLS_API_KEY=your_key

# Run tests
pytest tests/e2e/ -v -m "real_api"
```

## Expected Results

### Boulder, CO (Task 13.1)

**Expected composite score:** 80-90

- Strong innovation employment (CU Boulder, tech startups)
- High urban convenience (Pearl Street, downtown)
- Excellent outdoor access (trails, mountains)
- Moderate supply constraint (limited land)
- Low-moderate risk (some wildfire, minimal flood)

### Fort Collins, CO (Task 13.2)

**Expected composite score:** 75-85

- Good innovation employment (CSU, tech sector)
- Moderate urban convenience (smaller downtown)
- Very good outdoor access (trails, Horsetooth)
- Moderate supply constraint
- Low-moderate risk

### Boise, ID (Task 13.3)

**Expected composite score:** 70-85

- Growing innovation employment
- Good urban convenience
- Excellent outdoor access (mountains, trails)
- Moderate-high supply constraint (rapid growth)
- Moderate risk (wildfire in foothills)

## Test Coverage

Current E2E coverage:

- ✅ Market screening workflow
- ✅ Market analysis workflow
- ✅ Portfolio management workflow
- ✅ Cache operations workflow
- ⏳ Web GUI workflow (manual testing)
- ⏳ CLI workflow (manual testing)
- ⏳ Report generation (PDF/Excel)
- ⏳ State-specific rules (CO/UT/ID)

## CI/CD Integration

### GitHub Actions Workflow

```yaml
name: E2E Tests

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:      # Manual trigger

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install -e .[dev]
      - run: pytest tests/e2e/ -v
        env:
          CENSUS_API_KEY: ${{ secrets.CENSUS_API_KEY }}
          BLS_API_KEY: ${{ secrets.BLS_API_KEY }}
```

## Troubleshooting

### Test Failures

**API timeout:**

- Check internet connection
- Verify API keys are valid
- Increase timeout in config

**Unexpected scores:**

- Verify test market hasn't changed dramatically
- Check if API schemas have changed
- Review data source availability

**Cache issues:**

- Clear cache: `rm -rf .cache/`
- Check SQLite permissions
- Verify disk space

### Mock vs. Real Data

Tests are designed to work with **both mock and real data**:

- **Mock data**: Fast, reliable, no API keys needed
- **Real data**: Validates actual API integration

If an API call fails, tests will print a warning and use mock data
to continue the workflow test.

## Contributing

When adding new E2E tests:

1. **Focus on user workflows**, not individual functions
2. **Use real markets** with known expected results
3. **Handle failures gracefully** (mock data fallback)
4. **Document expected outcomes** in test docstrings
5. **Keep tests fast** (<30 seconds per test)

## Questions?

See:

- `TEST_STRATEGY.md` - Overall testing approach
- `MODULE_9_VERIFICATION.md` - Validation results
- `openspec/specs/*/spec.md` - Requirements specifications
