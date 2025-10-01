"""Mutation testing configuration for scoring engine.

This module validates that our tests can detect code mutations,
ensuring test effectiveness.
"""

import pytest

from Claude45_Demo.scoring_engine import ScoringEngine


class TestScoringEngineMutations:
    """Test scoring engine with mutation testing focus."""

    def test_weighted_average_calculation(self):
        """Test that weighted average is calculated correctly.

        This test should catch mutations like:
        - Changing * to +
        - Changing sum() to max()
        - Removing division
        """
        engine = ScoringEngine()

        # Test with known values
        scores = {
            "supply_constraint": 80.0,
            "innovation_employment": 60.0,
            "urban_convenience": 70.0,
            "outdoor_access": 90.0,
        }
        weights = {
            "supply_constraint": 0.3,
            "innovation_employment": 0.3,
            "urban_convenience": 0.2,
            "outdoor_access": 0.2,
        }

        result = engine.calculate_composite_score(scores, weights)

        # Expected: (80*0.3 + 60*0.3 + 70*0.2 + 90*0.2) = 24 + 18 + 14 + 18 = 74
        assert result["score"] == pytest.approx(74.0, abs=0.1)

        # Test mutation: changing operator
        assert result["score"] != 80.0  # Not just first score
        assert result["score"] != sum(scores.values())  # Not simple sum
        assert result["score"] != max(scores.values())  # Not max

    def test_normalization_bounds(self):
        """Test normalization maintains bounds.

        Should catch mutations to comparison operators.
        """
        engine = ScoringEngine()

        # Test lower bound
        result = engine.normalize_linear(-10.0, 0.0, 100.0)
        assert result == 0.0, "Below min should be clamped to 0"

        # Test upper bound
        result = engine.normalize_linear(150.0, 0.0, 100.0)
        assert result == 100.0, "Above max should be clamped to 100"

        # Test within range
        result = engine.normalize_linear(50.0, 0.0, 100.0)
        assert 0.0 < result < 100.0, "Within range should be normalized"

    def test_risk_adjustment_direction(self):
        """Test that risk adjustment works in correct direction.

        Should catch mutations to multiplication/division operators.
        """
        engine = ScoringEngine()

        base_score = 75.0

        # Test that risk adjustment is applied correctly
        # High risk multiplier (>1) should reduce effective score

        high_risk_result = engine.apply_risk_adjustment(base_score, 1.1)
        # Result dict should have adjusted_score lower than base
        assert high_risk_result["adjusted_score"] < base_score
        assert high_risk_result["original_score"] == base_score

        # Low risk should allow higher effective score
        low_risk_result = engine.apply_risk_adjustment(base_score, 0.9)
        assert low_risk_result["adjusted_score"] > base_score

        # Neutral risk should maintain score
        neutral_result = engine.apply_risk_adjustment(base_score, 1.0)
        assert neutral_result["adjusted_score"] == pytest.approx(base_score, abs=0.1)

