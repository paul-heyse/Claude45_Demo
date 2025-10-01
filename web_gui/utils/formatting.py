"""Data formatting utilities."""


def format_currency(value: float, decimals: int = 0) -> str:
    """Format value as currency.

    Args:
        value: Numeric value
        decimals: Number of decimal places

    Returns:
        Formatted currency string
    """
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.{decimals}f}B"
    elif value >= 1_000_000:
        return f"${value / 1_000_000:.{decimals}f}M"
    elif value >= 1_000:
        return f"${value / 1_000:.{decimals}f}K"
    else:
        return f"${value:.{decimals}f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format value as percentage.

    Args:
        value: Numeric value (0-100 or 0-1)
        decimals: Number of decimal places

    Returns:
        Formatted percentage string
    """
    # Handle both 0-1 and 0-100 ranges
    if value <= 1.0:
        value = value * 100
    return f"{value:.{decimals}f}%"


def format_score(value: float, decimals: int = 1) -> str:
    """Format score value.

    Args:
        value: Score value (0-100)
        decimals: Number of decimal places

    Returns:
        Formatted score string
    """
    return f"{value:.{decimals}f}"


def get_score_color(score: float) -> str:
    """Get color class for score value.

    Args:
        score: Score value (0-100)

    Returns:
        CSS class name for color
    """
    if score >= 81:
        return "score-excellent"  # Green
    elif score >= 61:
        return "score-good"  # Blue
    elif score >= 41:
        return "score-fair"  # Orange
    else:
        return "score-poor"  # Red


def get_score_color_hex(score: float) -> str:
    """Get hex color code for score value.

    Args:
        score: Score value (0-100)

    Returns:
        Hex color code
    """
    if score >= 81:
        return "#059669"  # Green
    elif score >= 61:
        return "#2563EB"  # Blue
    elif score >= 41:
        return "#D97706"  # Orange
    else:
        return "#DC2626"  # Red


def get_score_label(score: float) -> str:
    """Get label for score value.

    Args:
        score: Score value (0-100)

    Returns:
        Score label (Excellent, Good, Fair, Poor)
    """
    if score >= 81:
        return "Excellent"
    elif score >= 61:
        return "Good"
    elif score >= 41:
        return "Fair"
    else:
        return "Poor"


def format_risk_multiplier(value: float, decimals: int = 2) -> str:
    """Format risk multiplier value.

    Args:
        value: Risk multiplier (typically 0.7-1.3)
        decimals: Number of decimal places

    Returns:
        Formatted risk multiplier string
    """
    return f"{value:.{decimals}f}x"


def format_number(value: float, decimals: int = 0, compact: bool = False) -> str:
    """Format number with optional compact notation.

    Args:
        value: Numeric value
        decimals: Number of decimal places
        compact: Use compact notation (K, M, B)

    Returns:
        Formatted number string
    """
    if compact:
        if value >= 1_000_000_000:
            return f"{value / 1_000_000_000:.{decimals}f}B"
        elif value >= 1_000_000:
            return f"{value / 1_000_000:.{decimals}f}M"
        elif value >= 1_000:
            return f"{value / 1_000:.{decimals}f}K"

    return f"{value:,.{decimals}f}"
