"""Authentication utilities."""

from typing import Optional, Tuple

import streamlit as st


def authenticate_user(username: str, password: str) -> Tuple[bool, Optional[str]]:
    """Authenticate user with username and password.

    Args:
        username: User's email
        password: User's password

    Returns:
        Tuple of (success: bool, token: Optional[str])
    """
    # TODO: Implement actual authentication against backend
    # This is a simplified version for MVP

    # Demo credentials
    if username == "demo@aker.com" and password == "demo":
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.user_id = "demo_user"
        st.session_state.api_token = "demo_token_12345"
        return True, "demo_token_12345"

    return False, None


def check_auth() -> bool:
    """Check if user is authenticated.

    Returns:
        True if authenticated, False otherwise
    """
    return st.session_state.get("logged_in", False)


def require_auth(func):
    """Decorator to require authentication for a function.

    Args:
        func: Function to decorate

    Returns:
        Decorated function
    """

    def wrapper(*args, **kwargs):
        if not check_auth():
            st.warning("⚠️ Please login to access this page")
            st.stop()
        return func(*args, **kwargs)

    return wrapper


def logout():
    """Logout current user."""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_id = None
    st.session_state.api_token = None
    st.success("✓ Logged out successfully")
