"""Table component helpers."""

from typing import Any, Dict

import streamlit as st

from utils import get_score_color_hex, get_score_label


class MarketTable:
    """Reusable market table component."""

    def __init__(self, key_prefix: str = "table"):
        """Initialize market table.

        Args:
            key_prefix: Prefix for widget keys to avoid conflicts
        """
        self.key_prefix = key_prefix

    def render_header(self) -> None:
        """Render table header."""
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(
            [2, 1, 1, 1, 1, 1, 1, 1]
        )

        with col1:
            st.markdown("**Market**")
        with col2:
            st.markdown("**Score**")
        with col3:
            st.markdown("**Supply**")
        with col4:
            st.markdown("**Jobs**")
        with col5:
            st.markdown("**Urban**")
        with col6:
            st.markdown("**Outdoor**")
        with col7:
            st.markdown("**Risk**")
        with col8:
            st.markdown("**Actions**")

    def render_row(self, row: Dict[str, Any], idx: int) -> Dict[str, Any]:
        """Render a single market row.

        Args:
            row: Dictionary with market data
            idx: Row index for unique keys

        Returns:
            Dictionary with action results (view, add clicked)
        """
        actions = {"view": False, "add": False}

        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(
            [2, 1, 1, 1, 1, 1, 1, 1]
        )

        with col1:
            st.markdown(
                f"**{row['Market']}**<br>"
                f"<span style='color: #6B7280; font-size: 12px;'>{row['State']}</span>",
                unsafe_allow_html=True,
            )

        with col2:
            score_color = get_score_color_hex(row["Composite"])
            st.markdown(
                f"<div style='text-align: center;'>"
                f"<span style='color: {score_color}; font-size: 24px; font-weight: 600;'>{row['Composite']:.1f}</span>"
                f"<br><span style='font-size: 11px; color: #6B7280;'>{get_score_label(row['Composite'])}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

        with col3:
            st.markdown(
                f"<div style='text-align: center; font-size: 14px;'>{row['Supply']:.1f}</div>",
                unsafe_allow_html=True,
            )

        with col4:
            st.markdown(
                f"<div style='text-align: center; font-size: 14px;'>{row['Jobs']:.1f}</div>",
                unsafe_allow_html=True,
            )

        with col5:
            st.markdown(
                f"<div style='text-align: center; font-size: 14px;'>{row['Urban']:.1f}</div>",
                unsafe_allow_html=True,
            )

        with col6:
            st.markdown(
                f"<div style='text-align: center; font-size: 14px;'>{row['Outdoor']:.1f}</div>",
                unsafe_allow_html=True,
            )

        with col7:
            risk_color = (
                "#059669"
                if row["Risk"] < 1.0
                else "#DC2626" if row["Risk"] > 1.1 else "#D97706"
            )
            st.markdown(
                f"<div style='text-align: center; color: {risk_color}; font-weight: 600;'>{row['Risk']:.2f}x</div>",
                unsafe_allow_html=True,
            )

        with col8:
            col_a, col_b = st.columns(2)
            with col_a:
                actions["view"] = st.button(
                    "📍", key=f"{self.key_prefix}_view_{idx}", help="View Details"
                )
            with col_b:
                actions["add"] = st.button(
                    "➕", key=f"{self.key_prefix}_add_{idx}", help="Add to Portfolio"
                )

        return actions


def create_market_row(market_data: Dict[str, Any], key_prefix: str = "") -> None:
    """Create a formatted market row with scores.

    Args:
        market_data: Dictionary with market information
        key_prefix: Prefix for unique widget keys
    """
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        st.markdown(f"**{market_data.get('market', 'Unknown')}**")

    with col2:
        score = market_data.get("composite_score", 0)
        score_color = get_score_color_hex(score)
        st.markdown(
            f"<span style='color: {score_color}; font-size: 20px; font-weight: 600;'>{score:.1f}</span>",
            unsafe_allow_html=True,
        )

    with col3:
        risk = market_data.get("risk_multiplier", 1.0)
        st.markdown(f"{risk:.2f}x")

    with col4:
        if st.button("View", key=f"{key_prefix}_view"):
            st.info(f"Viewing details for {market_data.get('market')}")

