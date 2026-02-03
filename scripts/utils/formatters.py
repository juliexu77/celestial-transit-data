"""
JSON formatting and data structure utilities.
"""

import json
from datetime import datetime
from typing import Any, Dict


def get_zodiac_sign(longitude: float) -> tuple[str, float]:
    """
    Get zodiac sign and degree within sign from ecliptic longitude.

    Args:
        longitude: Ecliptic longitude in degrees (0-360)

    Returns:
        Tuple of (sign_name, degree_in_sign)
    """
    from lib.config import ZODIAC_SIGNS

    # Normalize longitude to 0-360 range
    longitude = longitude % 360

    # Each sign is 30 degrees
    sign_index = int(longitude / 30)
    degree_in_sign = longitude % 30

    return ZODIAC_SIGNS[sign_index], degree_in_sign


def format_datetime_iso(dt: datetime) -> str:
    """
    Format datetime as ISO 8601 string with UTC timezone.

    Args:
        dt: datetime object

    Returns:
        ISO 8601 formatted string (e.g., "2025-01-15T14:23:47Z")
    """
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def format_date_only(dt: datetime) -> str:
    """
    Format datetime as date-only string.

    Args:
        dt: datetime object

    Returns:
        Date string (e.g., "2025-01-15")
    """
    return dt.strftime("%Y-%m-%d")


def round_decimal(value: float, decimals: int = 6) -> float:
    """
    Round a float to specified decimal places.

    Args:
        value: Float value to round
        decimals: Number of decimal places (default 6)

    Returns:
        Rounded float
    """
    return round(value, decimals)


def save_json(data: Dict[str, Any], filepath: str, indent: int = 2) -> None:
    """
    Save data structure as formatted JSON file.

    Args:
        data: Data to save
        filepath: Path to output file
        indent: JSON indentation (default 2)
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def load_json(filepath: str) -> Dict[str, Any]:
    """
    Load JSON file into data structure.

    Args:
        filepath: Path to JSON file

    Returns:
        Loaded data structure
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)
