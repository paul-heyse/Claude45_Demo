"""Elevation and slope analysis utilities using DEM rasters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np


@dataclass(frozen=True)
class SlopeStatistics:
    """Summary statistics for slope analysis."""

    mean_slope: float
    max_slope: float
    flat_pct: float
    moderate_pct: float
    steep_pct: float


def calculate_slope_statistics(dem: np.ndarray, cell_size: float) -> SlopeStatistics:
    """Calculate slope statistics from a DEM grid using simple gradients."""

    if dem.ndim != 2:
        raise ValueError("DEM must be a 2D array")

    gy, gx = np.gradient(dem, cell_size)
    slope_radians = np.arctan(np.sqrt(gx**2 + gy**2))
    slope_degrees = np.degrees(slope_radians)

    mean_slope = float(np.mean(slope_degrees))
    max_slope = float(np.max(slope_degrees))

    flat_mask = slope_degrees < 5
    moderate_mask = (slope_degrees >= 5) & (slope_degrees <= 15)
    steep_mask = slope_degrees > 15

    total_cells = slope_degrees.size
    flat_pct = float(np.count_nonzero(flat_mask) / total_cells * 100)
    moderate_pct = float(np.count_nonzero(moderate_mask) / total_cells * 100)
    steep_pct = float(np.count_nonzero(steep_mask) / total_cells * 100)

    return SlopeStatistics(
        mean_slope=mean_slope,
        max_slope=max_slope,
        flat_pct=flat_pct,
        moderate_pct=moderate_pct,
        steep_pct=steep_pct,
    )


def calculate_aspect_distribution(
    dem: np.ndarray, cell_size: float
) -> Dict[str, float]:
    """Return percentage of dominant aspects (N/E/S/W)."""

    gy, gx = np.gradient(dem, cell_size)
    aspect = np.degrees(np.arctan2(gx, -gy))
    aspect = np.where(aspect < 0, aspect + 360, aspect)

    quadrants = {
        "N": ((aspect >= 315) | (aspect < 45)),
        "E": (aspect >= 45) & (aspect < 135),
        "S": (aspect >= 135) & (aspect < 225),
        "W": (aspect >= 225) & (aspect < 315),
    }

    total = aspect.size
    return {key: float(mask.sum() / total * 100) for key, mask in quadrants.items()}


def terrain_ruggedness_index(dem: np.ndarray, cell_size: float) -> float:
    """Calculate a simple Terrain Ruggedness Index scaled 0-100."""

    gy, gx = np.gradient(dem, cell_size)
    ruggedness = np.sqrt(gx**2 + gy**2)
    tri = float(np.mean(ruggedness))
    return max(0.0, min(tri * 25.0, 100.0))
