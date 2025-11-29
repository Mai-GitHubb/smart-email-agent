"""
Date parsing utilities for handling various date formats.
"""
from datetime import datetime, date
from typing import Optional
import re


def parse_date(date_str: str) -> Optional[date]:
    """
    Parse a date string in various formats to a date object.
    
    Handles formats like:
    - YYYY-MM-DD (ISO format)
    - Fri, 28 Nov, 2025
    - 28 Nov 2025
    - Nov 28, 2025
    - 2025-11-28
    - etc.
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        date object or None if parsing fails
    """
    if not date_str:
        return None
    
    date_str = date_str.strip()
    
    # Try ISO format first (YYYY-MM-DD)
    try:
        return datetime.fromisoformat(date_str).date()
    except (ValueError, AttributeError):
        pass
    
    # Try parsing with dateutil if available
    try:
        from dateutil import parser
        return parser.parse(date_str, fuzzy=True).date()
    except (ImportError, ValueError, AttributeError):
        pass
    
    # Manual parsing for common formats
    # Format: "Fri, 28 Nov, 2025" or "Fri, 28 Nov 2025"
    pattern1 = r'(\w+),\s*(\d+)\s+(\w+)[,\s]+(\d{4})'
    match = re.match(pattern1, date_str)
    if match:
        try:
            day_name, day, month_name, year = match.groups()
            month_map = {
                'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
            }
            month = month_map.get(month_name.lower()[:3])
            if month:
                return date(int(year), month, int(day))
        except (ValueError, KeyError):
            pass
    
    # Format: "28 Nov 2025" or "Nov 28, 2025"
    pattern2 = r'(\d+)\s+(\w+)\s+(\d{4})'
    match = re.match(pattern2, date_str)
    if match:
        try:
            day, month_name, year = match.groups()
            month_map = {
                'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
            }
            month = month_map.get(month_name.lower()[:3])
            if month:
                return date(int(year), month, int(day))
        except (ValueError, KeyError):
            pass
    
    # Format: "Nov 28, 2025"
    pattern3 = r'(\w+)\s+(\d+)[,\s]+(\d{4})'
    match = re.match(pattern3, date_str)
    if match:
        try:
            month_name, day, year = match.groups()
            month_map = {
                'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
            }
            month = month_map.get(month_name.lower()[:3])
            if month:
                return date(int(year), month, int(day))
        except (ValueError, KeyError):
            pass
    
    return None


def normalize_date(date_str: str) -> Optional[str]:
    """
    Normalize a date string to YYYY-MM-DD format.
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        Date string in YYYY-MM-DD format or None
    """
    date_obj = parse_date(date_str)
    if date_obj:
        return date_obj.isoformat()
    return None

