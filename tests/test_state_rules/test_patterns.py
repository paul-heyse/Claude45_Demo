"""
Tests for state regulatory pattern library.

Tests JSON-based jurisdiction patterns.
"""

from Claude45_Demo.state_rules.patterns import (
    get_jurisdiction_pattern,
    load_jurisdiction_patterns,
)


class TestJurisdictionPatterns:
    """Test jurisdiction regulatory pattern loading."""

    def test_load_all_patterns(self):
        """
        WHEN: Load jurisdiction patterns from JSON
        THEN: Return nested dict with CO/UT/ID data
        """
        patterns = load_jurisdiction_patterns()

        assert "colorado" in patterns
        assert "utah" in patterns
        assert "idaho" in patterns
        assert "Boulder" in patterns["colorado"]
        assert "Salt Lake City" in patterns["utah"]
        assert "Boise" in patterns["idaho"]

    def test_boulder_high_friction(self):
        """
        WHEN: Query Boulder CO pattern
        THEN: Return high permit days, design review, IZ
        """
        pattern = get_jurisdiction_pattern("colorado", "Boulder")

        assert pattern is not None
        assert pattern["median_permit_days"] > 180
        assert pattern["design_review_required"] is True
        assert pattern["inclusionary_zoning_pct"] >= 20

    def test_aurora_streamlined(self):
        """
        WHEN: Query Aurora CO pattern
        THEN: Return fast permits, no IZ
        """
        pattern = get_jurisdiction_pattern("colorado", "Aurora")

        assert pattern is not None
        assert pattern["median_permit_days"] < 60
        assert pattern["design_review_required"] is False
        assert pattern["inclusionary_zoning_pct"] == 0

    def test_utah_pro_development(self):
        """
        WHEN: Query Utah jurisdictions
        THEN: All have fast permits, no IZ (state-level pro-dev policy)
        """
        provo = get_jurisdiction_pattern("utah", "Provo")
        slc = get_jurisdiction_pattern("utah", "Salt Lake City")

        assert provo["median_permit_days"] < 90
        assert provo["inclusionary_zoning_pct"] == 0
        assert slc["median_permit_days"] < 120

    def test_idaho_streamlined(self):
        """
        WHEN: Query Idaho jurisdictions
        THEN: All have reasonable timelines, no IZ
        """
        boise = get_jurisdiction_pattern("idaho", "Boise")
        meridian = get_jurisdiction_pattern("idaho", "Meridian")

        assert boise["median_permit_days"] < 75
        assert meridian["median_permit_days"] < 60
        assert boise["inclusionary_zoning_pct"] == 0

    def test_unknown_jurisdiction(self):
        """
        WHEN: Query unknown jurisdiction
        THEN: Return None
        """
        result = get_jurisdiction_pattern("colorado", "UnknownCity")

        assert result is None
