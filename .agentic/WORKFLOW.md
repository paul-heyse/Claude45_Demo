# Agentic Development Workflow

Step-by-step workflow for AI-assisted development on the Aker Investment Platform.

## Pre-Development Checklist

Before starting any task:

- [ ] Read the relevant OpenSpec requirement in `openspec/changes/add-aker-investment-platform/specs/<capability>/spec.md`
- [ ] Review `.agentic/CONTEXT.md` for project patterns
- [ ] Check `.agentic/EXAMPLES.md` for similar code
- [ ] Ensure environment is activated: `micromamba activate ./.venv`
- [ ] Ensure tests pass: `pytest -q`

## Workflow Stages

### Stage 1: Understand the Requirement

**Input:** A task from `tasks.md` (e.g., "1.4 Build Census API connector")

**Steps:**

1. **Read the spec:**

   ```bash
   # Find the relevant spec
   cat openspec/changes/add-aker-investment-platform/specs/data-integration/spec.md | grep -A 20 "Census"
   ```

2. **Identify scenarios:**
   - Each `#### Scenario:` becomes a test case
   - WHEN clauses = test setup
   - THEN clauses = assertions

3. **Check design decisions:**

   ```bash
   cat openspec/changes/add-aker-investment-platform/design.md | grep -A 10 "Data Layer"
   ```

4. **Review similar code:**
   - Check `.agentic/EXAMPLES.md` for patterns
   - Look for existing connectors or similar functionality

### Stage 2: Write Tests First (TDD)

**Red-Green-Refactor cycle**

1. **Create test file:**

   ```bash
   touch tests/test_data_integration/test_census.py
   ```

2. **Write failing test based on spec scenario:**

   ```python
   # tests/test_data_integration/test_census.py

   def test_census_acs_demographic_retrieval(census_response):
       """
       Scenario: ACS demographic retrieval
       WHEN: System requests ACS 5-year estimates for a CBSA
       THEN: Returns DataFrame with population, income, education
       """
       connector = CensusConnector(api_key="test", cache=mock_cache)

       df = connector.fetch_acs(
           variables=["B01001_001E", "B19013_001E"],
           geography="county",
           geo_id="08031",  # Denver
           year=2021
       )

       # Assertions from THEN clauses
       assert isinstance(df, pd.DataFrame)
       assert "B01001_001E" in df.columns  # Population
       assert "B19013_001E" in df.columns  # Median income
       assert len(df) > 0
   ```

3. **Run test to confirm it fails:**

   ```bash
   pytest tests/test_data_integration/test_census.py::test_census_acs_demographic_retrieval -v
   # Expected: FAIL (module doesn't exist yet)
   ```

### Stage 3: Implement Minimum Viable

1. **Create module structure:**

   ```bash
   touch src/Claude45_Demo/data_integration/__init__.py
   touch src/Claude45_Demo/data_integration/census.py
   ```

2. **Implement just enough to pass the test:**

   ```python
   # src/Claude45_Demo/data_integration/census.py

   import pandas as pd
   from .base import APIConnector

   class CensusConnector(APIConnector):
       def fetch_acs(self, variables, geography, geo_id, year=2021):
           # Minimum implementation
           response = self._make_request(...)
           return self.parse(response)
   ```

3. **Run test:**

   ```bash
   pytest tests/test_data_integration/test_census.py::test_census_acs_demographic_retrieval -v
   # Goal: PASS
   ```

### Stage 4: Iterate on Remaining Scenarios

For each remaining scenario in the spec:

1. Write test
2. Run (expect fail)
3. Implement
4. Run (expect pass)
5. Refactor if needed

**Example iteration:**

```bash
# Scenario 2: Building permits query
pytest tests/test_data_integration/test_census.py::test_census_building_permits -v
# Implement feature...
pytest tests/test_data_integration/test_census.py::test_census_building_permits -v
```

### Stage 5: Integration Testing

Test the capability with other modules:

```python
# tests/integration/test_market_analysis_integration.py

def test_supply_constraint_with_real_census_data(mock_census_api):
    """Integration test: Census connector → Supply calculator"""

    # Set up
    cache = CacheManager()
    census = CensusConnector(api_key="test", cache=cache)
    supply_calc = SupplyConstraintCalculator(data_source=census)

    # Execute
    score = supply_calc.calculate_score(
        submarket=sample_submarket,
        reference_year=2021
    )

    # Verify
    assert 0 <= score <= 100
    assert hasattr(score, 'components')  # Can drill down
```

### Stage 6: Quality Checks

Run all quality checks:

```bash
# Tests
pytest -v --cov=src --cov-report=term-missing

# Linting
ruff check src tests

# Formatting
black src tests --check

# Type checking (if configured)
mypy src/

# All at once
pytest -v && ruff check src tests && black src tests --check
```

### Stage 7: Mark Complete

Update the task in `tasks.md`:

```markdown
## 1. Foundation & Data Integration

- [x] 1.1 Set up project dependencies
- [x] 1.2 Create base data integration framework
- [x] 1.3 Implement caching layer with SQLite backend
- [x] 1.4 Build Census API connector (ACS, Building Permits, BFS)
- [ ] 1.5 Build BLS API connector (CES, LAUS, QCEW)
```

Commit with conventional commit message:

```bash
git add src/Claude45_Demo/data_integration/census.py tests/test_data_integration/test_census.py
git commit -m "feat(data): add Census API connector

- Implement CensusConnector with ACS, BPS, BFS support
- Add caching and rate limiting
- Include tests for all scenarios in spec
- Resolves task 1.4

Refs: openspec/changes/add-aker-investment-platform/specs/data-integration/spec.md"
```

## Common Patterns

### Pattern: Adding a New Data Source

1. Read spec: `specs/data-integration/spec.md`
2. Create `src/Claude45_Demo/data_integration/<source>.py`
3. Inherit from `APIConnector` base class
4. Implement required methods: `fetch()`, `parse()`
5. Add caching via `CacheManager`
6. Write tests with mock responses
7. Add to `__init__.py` exports

### Pattern: Adding a New Scoring Function

1. Read spec: `specs/scoring-engine/spec.md` or `specs/market-analysis/spec.md`
2. Create function in appropriate module
3. Use normalization functions from `scoring_engine/normalization.py`
4. Write tests with known inputs/outputs
5. Document scoring formula in docstring
6. Return 0-100 score with component breakdown

### Pattern: Adding Geospatial Analysis

1. Read spec: `specs/geo-analysis/spec.md`
2. Use GeoPandas for vector operations
3. Use Shapely for geometry manipulation
4. Use proper CRS transformations (WGS84 ↔ UTM)
5. Test with known coordinates
6. Handle edge cases (empty results, API failures)

## Debugging Workflow

### When Tests Fail

1. **Read the error message carefully:**

   ```bash
   pytest tests/test_market_analysis/test_supply.py -v
   # Look for AssertionError, actual vs expected values
   ```

2. **Run with debugger:**

   ```bash
   pytest tests/test_market_analysis/test_supply.py -v --pdb
   # Drops into debugger on failure
   ```

3. **Print intermediate values:**

   ```python
   def test_supply_calculation():
       result = calculate_supply_score(...)
       print(f"DEBUG: result = {result}")  # Add temporary debug
       print(f"DEBUG: components = {result.components}")
       assert result > 50
   ```

4. **Check logs:**

   ```bash
   tail -f logs/aker_platform.log
   ```

### When API Integration Fails

1. **Check rate limits:**

   ```python
   # Look for RateLimitExceeded in logs
   tail logs/aker_platform.log | grep "rate limit"
   ```

2. **Inspect cache:**

   ```bash
   sqlite3 .cache/aker_platform.db
   SELECT key, created_at, expires_at FROM cache LIMIT 10;
   ```

3. **Test with mock first:**

   ```python
   @pytest.mark.unit
   def test_with_mock(mock_api_response):
       # Bypass API, test logic only
       pass

   @pytest.mark.integration
   def test_with_real_api():
       # Test actual API call
       pass
   ```

4. **Validate API response:**

   ```python
   response = connector.fetch(...)
   print(json.dumps(response, indent=2))  # Inspect structure
   ```

## Incremental Delivery Strategy

Build in thin vertical slices:

### Iteration 1: Proof of Concept

- One data source (Census)
- One metric (population)
- One score (supply constraint, simple version)
- CLI to run on one market
- **Goal:** End-to-end pipeline works

### Iteration 2: Market Analysis MVP

- Add 2-3 more data sources (BLS, EPA)
- Complete supply + jobs scoring
- Batch mode (5-10 markets)
- CSV export
- **Goal:** Useful for initial screening

### Iteration 3: Risk Layer

- Add FEMA flood, USFS wildfire
- Calculate risk multipliers
- Risk-adjusted scoring
- **Goal:** Underwriting-ready scores

### Iteration 4: Polish

- Full data source integration
- All scoring components
- Visualizations and reports
- **Goal:** Production-ready platform

## Agent-Specific Tips

### For AI Coding Assistants

1. **Always read the spec first** - Don't guess behavior
2. **Follow existing patterns** - Check `.agentic/EXAMPLES.md`
3. **Write tests before implementation** - Specs map directly to tests
4. **Use type hints** - Helps with code generation accuracy
5. **Generate complete examples** - Show how to use the code
6. **Handle errors explicitly** - Raise specific exceptions
7. **Log important events** - Use `logger.info/warning/error`
8. **Document assumptions** - Especially for proxies/estimates

### Prompt Engineering for Next Task

When ready for next task, provide this context:

```
I'm ready to implement task X.X from the Aker Investment Platform.

Context:
- Previous tasks completed: [list]
- Current task: [describe]
- Relevant spec: openspec/changes/add-aker-investment-platform/specs/<capability>/spec.md
- Existing patterns: .agentic/EXAMPLES.md
- Project structure: .agentic/CONTEXT.md

Please:
1. Read the relevant spec section
2. Show test structure for the scenarios
3. Implement the feature following project patterns
4. Run quality checks
5. Mark task complete in tasks.md
```

## Success Criteria

A task is complete when:

- [ ] All scenario tests pass
- [ ] Code coverage >80% for new code
- [ ] Linter passes (ruff check)
- [ ] Formatter passes (black --check)
- [ ] Type hints added (mypy if configured)
- [ ] Integration tests pass
- [ ] Docstrings added (Google style)
- [ ] Task marked [x] in tasks.md
- [ ] Committed with conventional commit message

---

**Remember:** The OpenSpec proposal is your source of truth. When in doubt, read the spec!
