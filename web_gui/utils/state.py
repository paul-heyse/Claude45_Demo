"""Session state management for Streamlit application."""

from datetime import datetime
from typing import Any, Dict

import streamlit as st


def initialize_session_state() -> None:
    """Initialize all session state variables with defaults."""

    # User session
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "api_token" not in st.session_state:
        st.session_state.api_token = None

    # Application state
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = datetime.now()

    # Data cache
    if "portfolio" not in st.session_state:
        st.session_state.portfolio = []
    if "screening_results" not in st.session_state:
        st.session_state.screening_results = []
    if "selected_market" not in st.session_state:
        st.session_state.selected_market = None
    if "cache_stats" not in st.session_state:
        st.session_state.cache_stats = {}

    # UI state
    if "filters" not in st.session_state:
        st.session_state.filters = {
            "supply_min": 0,
            "jobs_min": 0,
            "urban_min": 0,
            "outdoor_min": 0,
            "risk_max": 1.3,
        }
    if "sort_by" not in st.session_state:
        st.session_state.sort_by = "composite_score"
    if "sort_order" not in st.session_state:
        st.session_state.sort_order = "desc"
    if "page_number" not in st.session_state:
        st.session_state.page_number = 1
    if "selected_markets" not in st.session_state:
        st.session_state.selected_markets = []

    # Settings
    if "theme" not in st.session_state:
        st.session_state.theme = "light"
    if "map_style" not in st.session_state:
        st.session_state.map_style = "streets"
    if "results_per_page" not in st.session_state:
        st.session_state.results_per_page = 50


def clear_session_state() -> None:
    """Clear all session state variables."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    initialize_session_state()


def update_session_state(key: str, value: Any) -> None:
    """Update a session state variable.

    Args:
        key: Session state key
        value: New value
    """
    st.session_state[key] = value


def get_session_state(key: str, default: Any = None) -> Any:
    """Get a session state variable.

    Args:
        key: Session state key
        default: Default value if key doesn't exist

    Returns:
        Session state value or default
    """
    return st.session_state.get(key, default)


def save_filters(filters: Dict[str, Any]) -> None:
    """Save filter settings to session state.

    Args:
        filters: Dictionary of filter values
    """
    st.session_state.filters = filters


def load_filters() -> Dict[str, Any]:
    """Load filter settings from session state.

    Returns:
        Dictionary of filter values
    """
    return st.session_state.get(
        "filters",
        {
            "supply_min": 0,
            "jobs_min": 0,
            "urban_min": 0,
            "outdoor_min": 0,
            "risk_max": 1.3,
        },
    )
