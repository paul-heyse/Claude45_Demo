"""
Regulatory pattern library for state-specific rules.

Provides JSON-based pattern data for jurisdictional regulatory environments.
"""

import json
from pathlib import Path
from typing import Any


def load_jurisdiction_patterns() -> dict[str, Any]:
    """
    Load jurisdiction permit timeline and regulatory patterns.

    Returns:
        dict: Nested dict by state -> jurisdiction -> pattern data
    """
    pattern_file = Path(__file__).parent / "jurisdictions.json"
    with open(pattern_file) as f:
        return json.load(f)


def get_jurisdiction_pattern(state: str, jurisdiction: str) -> dict[str, Any] | None:
    """
    Get regulatory pattern for specific jurisdiction.

    Args:
        state: State code (lowercase: 'colorado', 'utah', 'idaho')
        jurisdiction: Municipality name

    Returns:
        dict | None: Pattern data or None if not found
    """
    patterns = load_jurisdiction_patterns()
    return patterns.get(state, {}).get(jurisdiction)
