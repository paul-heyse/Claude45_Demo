"""Tests for elevation and slope analysis module."""

from __future__ import annotations

import numpy as np

from Claude45_Demo.geo_analysis.elevation import (
    SlopeStatistics,
    calculate_aspect_distribution,
    calculate_slope_statistics,
    terrain_ruggedness_index,
)


def test_calculate_slope_statistics_classifies_categories() -> None:
    dem = np.array(
        [
            [1000, 1002, 1005, 1010],
            [999, 1001, 1004, 1011],
            [998, 999, 1002, 1008],
            [996, 998, 1001, 1005],
        ],
        dtype=float,
    )

    stats = calculate_slope_statistics(dem, cell_size=30.0)

    assert isinstance(stats, SlopeStatistics)
    assert stats.mean_slope > 0
    assert stats.max_slope > stats.mean_slope
    assert 0 <= stats.flat_pct + stats.moderate_pct + stats.steep_pct <= 100.5


def test_aspect_distribution_and_ruggedness() -> None:
    dem = np.array(
        [
            [1200, 1205, 1210],
            [1195, 1200, 1208],
            [1185, 1190, 1200],
        ],
        dtype=float,
    )

    distribution = calculate_aspect_distribution(dem, cell_size=10.0)
    assert abs(sum(distribution.values()) - 100) < 1e-6

    tri = terrain_ruggedness_index(dem, cell_size=10.0)
    assert 0 <= tri <= 100
    assert tri > 0
