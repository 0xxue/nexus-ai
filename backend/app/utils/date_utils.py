"""
Date Utilities

Simple date helpers. Complex natural language date parsing
("昨天", "上周") is handled by AI in the detect_intent node.
This module handles formatting and range calculations.
"""

from datetime import datetime, timedelta
from typing import Optional


def today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def yesterday() -> str:
    return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")


def days_ago(n: int) -> str:
    return (datetime.now() - timedelta(days=n)).strftime("%Y-%m-%d")


def date_range(start: str, end: str) -> list[str]:
    """Generate list of date strings between start and end (inclusive)."""
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.strptime(end, "%Y-%m-%d")
    dates = []
    current = s
    while current <= e:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    return dates


def this_week() -> tuple[str, str]:
    """Return (monday, today) of this week."""
    now = datetime.now()
    monday = now - timedelta(days=now.weekday())
    return monday.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")


def last_week() -> tuple[str, str]:
    """Return (monday, sunday) of last week."""
    now = datetime.now()
    last_monday = now - timedelta(days=now.weekday() + 7)
    last_sunday = last_monday + timedelta(days=6)
    return last_monday.strftime("%Y-%m-%d"), last_sunday.strftime("%Y-%m-%d")


def this_month() -> tuple[str, str]:
    """Return (first_day, today) of this month."""
    now = datetime.now()
    first = now.replace(day=1)
    return first.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")


def format_duration(seconds: int) -> str:
    """Format seconds into human-readable: 2h 30m 15s"""
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}h {minutes}m"
