"""Tests for unit mix optimizer."""

from Claude45_Demo.asset_evaluation.unit_mix import UnitMixOptimizer


def test_job_core_mix_biases_toward_smaller_units() -> None:
    optimizer = UnitMixOptimizer()
    rec = optimizer.recommend(
        {
            "job_core": True,
            "daytime_population_index": 140,
            "rent_burden": 25,
        }
    )

    assert rec.mix["studio"] + rec.mix["one_bed"] >= 0.6
    assert "job core" in rec.rationale.lower() or "compact" in rec.rationale.lower()


def test_family_node_mixes_larger_units_with_affordability_adjustment() -> None:
    optimizer = UnitMixOptimizer()
    rec = optimizer.recommend(
        {
            "family_age_cohort_index": 120,
            "schools_rating": 8,
            "outdoor_access_score": 80,
            "rent_burden": 38,
            "inclusionary_zoning": True,
        }
    )

    assert rec.mix["two_bed"] + rec.mix["three_bed"] >= 0.5
    assert rec.mix["studio"] >= 0.1  # affordability adjustment
