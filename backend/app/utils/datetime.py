"""
Datetime utility functions.
"""
from datetime import datetime
from typing import Optional


def format_datetime_utc(dt: Optional[datetime]) -> Optional[str]:
    """
    Format datetime as ISO 8601 with UTC timezone indicator.

    Args:
        dt: Datetime object to format.

    Returns:
        ISO 8601 formatted string with 'Z' suffix, or None if dt is None.
    """
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"
