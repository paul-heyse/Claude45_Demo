"""Tests for product type classification and Aker fit scoring."""

from __future__ import annotations

import pytest


class TestProductTypeClassification:
    """Test multifamily product type identification."""

    def test_garden_style_classification(self, product_classifier):
        """Test garden-style (1-2 stories, surface parking) classification."""
        property_data = {
            "stories": 2,
            "parking_type": "surface",
            "building_count": 8,
            "units": 120,
            "unit_density": 15,  # units per acre
        }

        result = product_classifier.classify_product_type(property_data)

        assert result["product_type"] == "garden"
        assert result["aker_fit_score"] == 100  # Garden is 100% fit
        assert result["description"] == "Garden-style (1-2 stories, surface parking)"
        assert result["typical_features"] == [
            "Surface parking",
            "Lower density",
            "Outdoor-oriented",
        ]

    def test_low_rise_classification(self, product_classifier):
        """Test low-rise (3-4 stories) classification."""
        property_data = {
            "stories": 4,
            "parking_type": "tuck-under",
            "building_count": 2,
            "units": 80,
            "unit_density": 40,
        }

        result = product_classifier.classify_product_type(property_data)

        assert result["product_type"] == "low-rise"
        assert result["aker_fit_score"] == 100  # Low-rise is 100% fit
        assert "3-4 stories" in result["description"]

    def test_mid_rise_selective_fit(self, product_classifier):
        """Test mid-rise (5-8 stories) with selective 70% fit."""
        property_data = {
            "stories": 6,
            "parking_type": "structured",
            "building_count": 1,
            "units": 120,
            "unit_density": 80,
        }

        result = product_classifier.classify_product_type(property_data)

        assert result["product_type"] == "mid-rise"
        assert result["aker_fit_score"] == 70  # Mid-rise is selective
        assert "5-8 stories" in result["description"]
        assert result["notes"] == "Select opportunities only"

    def test_high_rise_rare_fit(self, product_classifier):
        """Test high-rise (9+ stories) with 20% rare fit."""
        property_data = {
            "stories": 12,
            "parking_type": "structured",
            "building_count": 1,
            "units": 200,
            "unit_density": 150,
        }

        result = product_classifier.classify_product_type(property_data)

        assert result["product_type"] == "high-rise"
        assert result["aker_fit_score"] == 20  # High-rise is rare
        assert "9+ stories" in result["description"]
        assert result["notes"] == "Rare opportunity, high bar"


class TestMixedUseAssessment:
    """Test mixed-use property evaluation."""

    def test_mixed_use_town_center_high_fit(self, product_classifier):
        """Test mixed-use in walkable town center (high fit)."""
        property_data = {
            "stories": 4,
            "ground_floor_commercial": True,
            "commercial_sf": 8000,
            "residential_units": 60,
            "location_type": "town_center",
            "walk_score": 85,
            "retail_tenants": ["coffee_shop", "outdoor_gear", "bodega"],
        }

        result = product_classifier.assess_mixed_use(property_data)

        assert result["is_mixed_use"] is True
        assert result["location_fit"] == "high"  # Town center
        assert result["retail_profile_score"] >= 80  # Preferred tenants
        assert result["mixed_use_fit_score"] >= 85
        assert "preferred tenants: 3/3" in result["retail_assessment"].lower()

    def test_mixed_use_auto_oriented_low_fit(self, product_classifier):
        """Test mixed-use in auto-oriented area (lower fit)."""
        property_data = {
            "stories": 3,
            "ground_floor_commercial": True,
            "commercial_sf": 5000,
            "residential_units": 40,
            "location_type": "suburban",
            "walk_score": 35,
            "retail_tenants": ["chain_restaurant", "dry_cleaner"],
        }

        result = product_classifier.assess_mixed_use(property_data)

        assert result["is_mixed_use"] is True
        assert result["location_fit"] == "low"  # Auto-oriented
        assert result["retail_profile_score"] < 60  # Not preferred tenants
        assert result["mixed_use_fit_score"] < 50

    def test_residential_only_not_mixed_use(self, product_classifier):
        """Test that residential-only property is not flagged as mixed-use."""
        property_data = {
            "stories": 3,
            "ground_floor_commercial": False,
            "residential_units": 80,
            "location_type": "urban",
        }

        result = product_classifier.assess_mixed_use(property_data)

        assert result["is_mixed_use"] is False
        assert result["mixed_use_fit_score"] == 0


class TestAdaptiveReuseEvaluation:
    """Test adaptive reuse potential assessment."""

    def test_office_to_residential_high_potential(self, product_classifier):
        """Test office building with high conversion potential."""
        property_data = {
            "current_use": "office",
            "year_built": 1985,
            "stories": 5,
            "ceiling_height_ft": 10,
            "floor_plate_sf": 15000,
            "window_to_floor_ratio": 0.25,  # Good natural light
            "location_type": "urban",
        }

        result = product_classifier.evaluate_adaptive_reuse(property_data)

        assert result["reuse_candidate"] is True
        assert result["conversion_complexity"] == "low"  # Good specs = low complexity
        assert result["reuse_potential_score"] >= 70
        assert any("ceiling height" in f.lower() for f in result["positive_factors"])
        assert any("natural light" in f.lower() for f in result["positive_factors"])

    def test_industrial_conversion_low_potential(self, product_classifier):
        """Test industrial building with lower conversion feasibility."""
        property_data = {
            "current_use": "warehouse",
            "year_built": 1975,
            "stories": 1,
            "ceiling_height_ft": 20,  # Too high
            "floor_plate_sf": 50000,  # Too large
            "window_to_floor_ratio": 0.05,  # Poor natural light
            "location_type": "industrial",
        }

        result = product_classifier.evaluate_adaptive_reuse(property_data)

        assert result["reuse_candidate"] is True  # Still a candidate
        assert result["conversion_complexity"] == "high"
        assert result["reuse_potential_score"] < 50
        assert "floor plate" in str(result["challenges"]).lower()

    def test_non_convertible_property(self, product_classifier):
        """Test property not suitable for conversion."""
        property_data = {
            "current_use": "multifamily",  # Already residential
            "year_built": 2010,
            "stories": 4,
        }

        result = product_classifier.evaluate_adaptive_reuse(property_data)

        assert result["reuse_candidate"] is False
        assert result["reuse_potential_score"] == 0
        assert "already residential" in result["notes"].lower()


class TestProductMetadata:
    """Test product type metadata and documentation."""

    def test_metadata_includes_all_fields(self, product_classifier):
        """Test that classification includes comprehensive metadata."""
        property_data = {
            "stories": 3,
            "parking_type": "tuck-under",
            "units": 60,
        }

        result = product_classifier.classify_product_type(property_data)

        # Check all required metadata fields present
        assert "product_type" in result
        assert "aker_fit_score" in result
        assert "description" in result
        assert "typical_features" in result
        assert isinstance(result["typical_features"], list)

    def test_fit_score_range_validation(self, product_classifier):
        """Test that fit scores are always in 0-100 range."""
        test_cases = [
            {"stories": 1},  # Garden
            {"stories": 4},  # Low-rise
            {"stories": 6},  # Mid-rise
            {"stories": 12},  # High-rise
        ]

        for property_data in test_cases:
            result = product_classifier.classify_product_type(property_data)
            assert 0 <= result["aker_fit_score"] <= 100


@pytest.fixture
def product_classifier():
    """Create ProductTypeClassifier instance for testing."""
    from Claude45_Demo.asset_evaluation.product_type import ProductTypeClassifier

    return ProductTypeClassifier()
