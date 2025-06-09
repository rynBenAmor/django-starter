from django import template
from decimal import Decimal
import math

"""
Math Helper Template Tags and Filters

Filters:
    percentage_of(value, max_value) -> float
        Calculate percentage (value/max_value * 100)
        Example: {{ stock|percentage_of:max_stock }}

    subtract(value, arg) -> float
        Subtract arg from value
        Example: {{ total|subtract:discount }}

    multiply(value, arg) -> float
        Multiply value by arg
        Example: {{ price|multiply:quantity }}

    divide(value, arg) -> float
        Divide value by arg
        Example: {{ total|divide:12 }}

    round_number(value, decimals=0) -> float
        Round to specified decimal places
        Example: {{ price|round_number:2 }}

    ceil(value) -> int
        Round up to nearest integer
        Example: {{ rating|ceil }}

    floor(value) -> int
        Round down to nearest integer
        Example: {{ rating|floor }}

    absolute(value) -> float
        Return absolute value
        Example: {{ temperature|absolute }}

    intify(value) -> int
        tries to convert a value into an int
        Example: {{ average|intify }}

    modulo(value, arg) -> int
        Return value modulo arg
        Example: {% if forloop.counter|modulo:2 == 0 %} Even {% endif %}
    
    max_of(value, arg) -> number
        Return the greater of two values

    min_of(value, arg) -> number
        Return the smaller of two values
    
    as_currency(value, symbol="$") -> string
        Example: {{ product.price|as_currency:"£" }}
        Returns: "£3.00"


Tags:
    {% calculate_discount price discount_percent %}
        Calculate price after discount
        Example: {% calculate_discount product.price 15 %}

    {% price_range min_price max_price decimals=2 %}
        Format a price range
        Example: {% price_range product.min_price product.max_price 2 %}
"""

register = template.Library()


@register.filter
def percentage_of(value, max_value):
    """Calculate percentage of value relative to max_value"""
    try:
        return (float(value) / float(max_value)) * 100
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def subtract(value, arg):
    """Subtract arg from value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def multiply(value, arg):
    """Multiply value by arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def divide(value, arg):
    """Divide value by arg"""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError, TypeError):
        return 0

@register.filter
def round_number(value, decimals=0):
    """Round a number to specified decimal places"""
    try:
        return round(float(value), int(decimals))
    except (ValueError, TypeError):
        return 0

@register.filter
def ceil(value):
    """Round up to nearest integer"""
    try:
        return math.ceil(float(value))
    except (ValueError, TypeError):
        return 0

@register.filter
def floor(value):
    """Round down to nearest integer"""
    try:
        return math.floor(float(value))
    except (ValueError, TypeError):
        return 0

@register.simple_tag
def calculate_discount(price, discount_percent):
    """Calculate discounted price"""
    try:
        price = float(price)
        discount = float(discount_percent)
        return price - (price * (discount / 100))
    except (ValueError, TypeError):
        return price

@register.simple_tag
def price_range(min_price, max_price, decimals=2):
    """Format a price range"""
    try:
        min_p = round(float(min_price), decimals)
        max_p = round(float(max_price), decimals)
        if min_p == max_p:
            return f"{min_p}"
        return f"{min_p} - {max_p}"
    except (ValueError, TypeError):
        return "N/A"

@register.filter
def absolute(value):
    """Return absolute value"""
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return 0


@register.filter
def intify(value):
    """Safely convert a value to int. Returns 0 on failure."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

@register.filter
def modulo(value, arg):
    """Return value modulo arg. Returns 0 on error (or divide by 0)."""
    try:
        return int(value) % int(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def max_of(value, arg):
    """Return the maximum of two numeric values."""
    try:
        return max(float(value), float(arg))
    except (ValueError, TypeError):
        return 0

@register.filter
def min_of(value, arg):
    """Return the minimum of two numeric values."""
    try:
        return min(float(value), float(arg))
    except (ValueError, TypeError):
        return 0


@register.filter
def as_currency(value, symbol="$"):
    try:
        return f"{symbol}{float(value):,.2f}"
    except (ValueError, TypeError):
        return f"{symbol}0.00"
