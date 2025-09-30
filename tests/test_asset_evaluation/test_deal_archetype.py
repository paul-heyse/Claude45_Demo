"""Tests for deal archetype classifier."""

from Claude45_Demo.asset_evaluation.deal_archetype import DealArchetypeClassifier


def test_classify_value_add_light() -> None:
    classifier = DealArchetypeClassifier()
    result = classifier.classify(
        {
            "year_built": 2005,
            "occupancy": 0.92,
            "deferred_maintenance_score": 2,
            "systems_condition": "good",
            "location_type": "town_center",
        }
    )

    assert result.archetype == "value_add_light"
    assert 80 <= result.score <= 95
    assert result.rent_lift_range == (90, 180)


def test_classify_ground_up_identifies_spread() -> None:
    classifier = DealArchetypeClassifier()
    result = classifier.classify(
        {
            "is_vacant_land": True,
            "yield_on_cost": 6.3,
            "stabilized_cap_rate": 4.5,
            "entitlement_complexity": "high",
        }
    )

    assert result.archetype == "ground_up_infill"
    assert "Entitlement complexity high" in result.risk_notes


def test_classify_heavy_lift_records_risks() -> None:
    classifier = DealArchetypeClassifier()
    result = classifier.classify(
        {
            "year_built": 1970,
            "occupancy": 0.55,
            "deferred_maintenance_score": 8,
            "systems_condition": "poor",
        }
    )

    assert result.archetype == "heavy_lift_reposition"
    assert result.risk_notes
