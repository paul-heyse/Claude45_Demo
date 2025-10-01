"""Filter component helpers."""

from typing import Dict

import streamlit as st


class FilterPanel:
    """Reusable filter panel for market screening."""

    def __init__(self, key_prefix: str = "filter"):
        """Initialize filter panel.

        Args:
            key_prefix: Prefix for widget keys to avoid conflicts
        """
        self.key_prefix = key_prefix

    def render_score_filters(self) -> Dict[str, float]:
        """Render score filter sliders.

        Returns:
            Dictionary of filter values
        """
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Score Filters**")
            supply_min = st.slider(
                "Supply Constraint (min)",
                0,
                100,
                0,
                key=f"{self.key_prefix}_supply",
                help="Minimum supply constraint score (0-100)",
            )

            jobs_min = st.slider(
                "Innovation Jobs (min)",
                0,
                100,
                0,
                key=f"{self.key_prefix}_jobs",
                help="Minimum innovation employment score (0-100)",
            )

            urban_min = st.slider(
                "Urban Convenience (min)",
                0,
                100,
                0,
                key=f"{self.key_prefix}_urban",
                help="Minimum urban convenience score (0-100)",
            )

        with col2:
            st.markdown("**Risk & Location**")
            risk_max = st.slider(
                "Risk Multiplier (max)",
                0.7,
                1.3,
                1.3,
                0.05,
                key=f"{self.key_prefix}_risk",
                help="Maximum acceptable risk multiplier",
            )

            outdoor_min = st.slider(
                "Outdoor Access (min)",
                0,
                100,
                0,
                key=f"{self.key_prefix}_outdoor",
                help="Minimum outdoor access score (0-100)",
            )

            composite_min = st.slider(
                "Composite Score (min)",
                0,
                100,
                0,
                key=f"{self.key_prefix}_composite",
                help="Minimum composite score (0-100)",
            )

        return {
            "supply_min": supply_min,
            "jobs_min": jobs_min,
            "urban_min": urban_min,
            "outdoor_min": outdoor_min,
            "risk_max": risk_max,
            "composite_min": composite_min,
        }


def create_score_filter(
    label: str,
    key: str,
    min_value: int = 0,
    max_value: int = 100,
    default: int = 0,
    help_text: str = "",
) -> int:
    """Create a single score filter slider.

    Args:
        label: Filter label
        key: Unique key for widget
        min_value: Minimum slider value
        max_value: Maximum slider value
        default: Default value
        help_text: Help tooltip text

    Returns:
        Selected value
    """
    return st.slider(
        label,
        min_value=min_value,
        max_value=max_value,
        value=default,
        key=key,
        help=help_text,
    )

