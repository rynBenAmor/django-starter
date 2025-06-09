from django import template
from datetime import datetime, timedelta, date

register = template.Library()

@register.filter
def days_ago(value):
    """
    Returns the number of days ago from today.
    Usage: {{ some_date|days_ago }}
    """
    if not value:
        return ''
    today = date.today()
    if isinstance(value, datetime):
        value = value.date()
    delta = today - value
    return delta.days

@register.filter
def is_today(value):
    """
    Returns True if the date is today.
    Usage: {% if some_date|is_today %}
    """
    if not value:
        return False
    today = date.today()
    if isinstance(value, datetime):
        value = value.date()
    return value == today

@register.filter
def is_yesterday(value):
    """
    Returns True if the date is yesterday.
    Usage: {% if some_date|is_yesterday %}
    """
    if not value:
        return False
    today = date.today()
    if isinstance(value, datetime):
        value = value.date()
    return value == today - timedelta(days=1)

@register.filter
def is_this_week(value):
    """
    Returns True if the date is in the current week.
    Usage: {% if some_date|is_this_week %}
    """
    if not value:
        return False
    today = date.today()
    if isinstance(value, datetime):
        value = value.date()
    return value.isocalendar()[1] == today.isocalendar()[1] and value.year == today.year

@register.filter
def add_days(value, days):
    """
    Adds days to a date.
    Usage: {{ some_date|add_days:3 }}
    """
    try:
        days = int(days)
        if isinstance(value, datetime):
            return value + timedelta(days=days)
        elif isinstance(value, date):
            return value + timedelta(days=days)
    except Exception:
        return value

@register.filter
def subtract_days(value, days):
    """
    Subtracts days from a date.
    Usage: {{ some_date|subtract_days:7 }}
    """
    try:
        days = int(days)
        if isinstance(value, datetime):
            return value - timedelta(days=days)
        elif isinstance(value, date):
            return value - timedelta(days=days)
    except Exception:
        return value

@register.filter
def to_iso(value):
    """
    Returns ISO 8601 string for a date/datetime.
    Usage: {{ some_date|to_iso }}
    """
    try:
        return value.isoformat()
    except Exception:
        return value

@register.filter
def weekday_name(value):
    """
    Returns the weekday name (e.g., Monday).
    Usage: {{ some_date|weekday_name }}
    """
    try:
        if isinstance(value, datetime):
            value = value.date()
        return value.strftime('%A')
    except Exception:
        return ''

@register.filter
def month_name(value):
    """
    Returns the month name (e.g., January).
    Usage: {{ some_date|month_name }}
    """
    try:
        if isinstance(value, datetime):
            value = value.date()
        return value.strftime('%B')
    except Exception:
        return ''

@register.filter
def year(value):
    """
    Returns the year of the date.
    Usage: {{ some_date|year }}
    """
    try:
        if isinstance(value, datetime):
            value = value.date()
        return value.year
    except Exception:
        return ''

@register.filter
def date_diff(value, other):
    """
    Returns the difference in days between two dates.
    Usage: {{ date1|date_diff:date2 }}
    """
    try:
        if isinstance(value, datetime):
            value = value.date()
        if isinstance(other, datetime):
            other = other.date()
        return (value - other).days
    except Exception:
        return ''