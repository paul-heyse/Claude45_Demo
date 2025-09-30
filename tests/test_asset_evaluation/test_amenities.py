"""Tests for amenity scoring utilities."""

from Claude45_Demo.asset_evaluation.amenities import AmenityScores, evaluate_amenities


def test_outdoor_brand_scoring_counts_features() -> None:
    scores = evaluate_amenities(
        outdoor_features={
            "balconies": True,
            "gear_storage": True,
            "bike_ski_storage": True,
            "dog_wash": True,
            "mudroom": False,
        },
        unique_outdoor_features=["bike_tune_bench"],
        ev_data={
            "existing_ev_stalls": 6,
            "total_stalls": 60,
            "ev_ready_conduit": True,
        },
        remote_work_features={
            "quiet_rooms": True,
            "micro_offices": True,
            "mesh_wifi": True,
        },
        monetization_potential=True,
        pet_features={
            "dog_run": True,
            "dog_wash": True,
            "pet_policy_friendly": True,
        },
        pet_policy={"no_breed_restrictions": True},
    )

    assert isinstance(scores, AmenityScores)
    assert scores.outdoor_brand_score >= 80
    assert scores.ev_readiness_score >= 60
    assert scores.remote_work_score >= 80
    assert scores.pet_friendliness_score > 70


def test_ev_readiness_handles_no_parking() -> None:
    scores = evaluate_amenities(
        outdoor_features={},
        unique_outdoor_features=None,
        ev_data={"existing_ev_stalls": 0, "total_stalls": 0, "ev_ready_conduit": False},
        remote_work_features={},
        monetization_potential=False,
        pet_features={},
        pet_policy={},
    )

    assert scores.ev_readiness_score == 0
