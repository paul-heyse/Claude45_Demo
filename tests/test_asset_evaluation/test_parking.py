"""Tests for parking advisor."""

from Claude45_Demo.asset_evaluation.parking import ParkingAdvisor


def test_infill_transit_reduces_ratio() -> None:
    advisor = ParkingAdvisor()
    rec = advisor.recommend(
        {
            "location_type": "urban_core",
            "transit_headway_minutes": 12,
            "acs_vehicle_per_household": 0.8,
            "zoning_minimum": 0.75,
            "unbundled_parking": True,
        }
    )

    assert rec.recommended_ratio < 0.7
    assert "Transit headway" in rec.rationale


def test_suburban_defaults_higher() -> None:
    advisor = ParkingAdvisor()
    rec = advisor.recommend(
        {
            "location_type": "suburban",
            "transit_headway_minutes": 30,
            "acs_vehicle_per_household": 1.6,
            "zoning_minimum": 1.2,
        }
    )

    assert rec.recommended_ratio >= 1.1
    assert "zoning" in rec.zoning_check.lower()
