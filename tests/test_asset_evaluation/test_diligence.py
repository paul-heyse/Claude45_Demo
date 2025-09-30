"""Tests for diligence checklist builder."""

from Claude45_Demo.asset_evaluation.diligence import DiligenceChecklistBuilder


def test_value_add_checklist_includes_aker_items() -> None:
    builder = DiligenceChecklistBuilder()
    checklist = builder.build(
        archetype="value_add_light",
        product_type="garden",
        risk_flags={"wildfire": False, "flood": False},
        include_ev=True,
    )

    assert "Scope interior upgrade pricing per unit" in checklist["physical"]
    assert any("EV" in item for item in checklist["amenities"])


def test_high_risk_adds_mitigation_section() -> None:
    builder = DiligenceChecklistBuilder()
    checklist = builder.build(
        archetype="heavy_lift_reposition",
        product_type="mid-rise",
        risk_flags={"wildfire": True, "flood": True},
        include_ev=False,
    )

    assert "risk_mitigation" in checklist
    assert any("Insurance" in item for item in checklist["risk_mitigation"])
