"""Property-based tests using Hypothesis.

These tests explore the input space automatically to find edge cases.
"""

import pytest
from hypothesis import given, strategies as st, assume

from Claude45_Demo.scoring_engine import ScoringEngine


class TestScoringProperties:
    """Property-based tests for scoring engine."""

    @given(st.floats(min_value=0.0, max_value=100.0))
    def test_normalization_always_in_range(self, value):
        """Test that normalization always produces values in [0, 100]."""
        engine = ScoringEngine()

        result = engine.normalize_linear(value, 0.0, 100.0)

        assert 0.0 <= result <= 100.0, f"Normalized {value} to {result}, out of range"

    @given(
        st.floats(min_value=-1000.0, max_value=1000.0),
        st.floats(min_value=0.0, max_value=100.0),
        st.floats(min_value=100.0, max_value=200.0),
    )
    def test_normalization_with_any_bounds(self, value, min_val, max_val):
        """Test normalization with various min/max bounds."""
        assume(min_val < max_val)  # Skip invalid cases

        engine = ScoringEngine()
        result = engine.normalize_linear(value, min_val, max_val)

        # Result should always be in [0, 100]
        assert 0.0 <= result <= 100.0

    @given(
        score=st.floats(min_value=0.0, max_value=100.0),
        risk_multiplier=st.floats(min_value=0.8, max_value=1.2),
    )
    def test_risk_adjustment_preserves_score_range(self, score, risk_multiplier):
        """Test that risk adjustment keeps scores in valid range."""
        engine = ScoringEngine()

        result = engine.apply_risk_adjustment(score, risk_multiplier)

        # Adjusted score should stay in reasonable range
        assert -10.0 <= result["adjusted_score"] <= 110.0

    @given(
        supply=st.floats(min_value=0.0, max_value=100.0),
        innovation=st.floats(min_value=0.0, max_value=100.0),
        urban=st.floats(min_value=0.0, max_value=100.0),
        outdoor=st.floats(min_value=0.0, max_value=100.0),
    )
    def test_composite_score_properties(self, supply, innovation, urban, outdoor):
        """Test composite score invariants."""
        engine = ScoringEngine()

        scores = {
            "supply_constraint": supply,
            "innovation_employment": innovation,
            "urban_convenience": urban,
            "outdoor_access": outdoor,
        }

        result = engine.calculate_composite_score(scores)

        # Composite should be weighted average, so between min and max
        min_score = min(scores.values())
        max_score = max(scores.values())

        assert min_score <= result["score"] <= max_score, \
            f"Composite {result['score']} not between {min_score} and {max_score}"

    @given(st.floats(min_value=0.0, max_value=100.0))
    def test_percentile_normalization_monotonic(self, value):
        """Test that percentile normalization is monotonic."""
        engine = ScoringEngine()

        # Create reference distribution
        reference_values = [10.0, 30.0, 50.0, 70.0, 90.0]

        result1 = engine.normalize_percentile(value, reference_values)

        # Adding higher value should increase or maintain percentile
        result2 = engine.normalize_percentile(value + 10.0, reference_values)

        assert result2["score"] >= result1["score"], \
            "Percentile normalization should be monotonic"


class TestMarketAnalysisProperties:
    """Property-based tests for market analysis."""

    @given(
        permits_per_1k=st.floats(min_value=0.0, max_value=50.0),
    )
    def test_supply_constraint_non_negative(self, permits_per_1k):
        """Test that supply constraint score is always non-negative."""
        from Claude45_Demo.market_analysis import SupplyConstraintCalculator

        calc = SupplyConstraintCalculator()

        # Lower permits = higher constraint score
        # Should never be negative
        result = calc.calculate_permit_elasticity(
            permits_per_1k_households=permits_per_1k,
            national_avg=10.0
        )

        assert result["score"] >= 0.0
        assert result["score"] <= 100.0

    @given(
        local_lq=st.floats(min_value=0.0, max_value=5.0),
        local_cagr=st.floats(min_value=-0.1, max_value=0.3),
    )
    def test_employment_score_bounds(self, local_lq, local_cagr):
        """Test employment score stays within bounds."""
        from Claude45_Demo.market_analysis import EmploymentAnalyzer

        analyzer = EmploymentAnalyzer()

        sector_lq = {"tech": local_lq}
        sector_cagr = {"tech": local_cagr}

        result = analyzer.calculate_innovation_employment_score(
            sector_cagr, sector_lq
        )

        assert 0.0 <= result["score"] <= 100.0


class TestRiskAssessmentProperties:
    """Property-based tests for risk assessment."""

    @given(
        wildfire_score=st.floats(min_value=0.0, max_value=100.0),
        flood_score=st.floats(min_value=0.0, max_value=100.0),
        seismic_score=st.floats(min_value=0.0, max_value=100.0),
    )
    def test_risk_multiplier_bounds(self, wildfire_score, flood_score, seismic_score):
        """Test that risk multiplier stays in reasonable range."""
        from Claude45_Demo.risk_assessment import RiskMultiplierCalculator

        calc = RiskMultiplierCalculator()

        result = calc.calculate_composite_multiplier({
            "wildfire_score": wildfire_score,
            "flood_score": flood_score,
            "seismic_score": seismic_score,
        })

        # Risk multiplier should be in reasonable range
        # 0.7 (30% discount) to 1.3 (30% premium)
        assert 0.7 <= result["risk_multiplier"] <= 1.3


if __name__ == "__main__":
    # Run property-based tests with more examples
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])

