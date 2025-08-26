from django import template
from django.utils.html import strip_tags as dj_strip_tags
from django.utils.text import slugify as dj_slugify
from django.utils.html import strip_tags
import html
import re



register = template.Library()

@register.filter
def truncate_chars(value, n):
    """
    Truncate string to n characters, adding ellipsis if needed.
    Usage: {{ value|truncate_chars:20 }}
    """
    try:
        n = int(n)
        value = str(value)
        return value[:n] + ('…' if len(value) > n else '')
    except Exception:
        return value

@register.filter
def truncate_words(value, num):
    """
    Truncate string to n words, adding ellipsis if needed.
    Usage: {{ value|truncate_words:10 }}
    """
    try:
        num = int(num)
        words = str(value).split()
        return ' '.join(words[:num]) + ('...' if len(words) > num else '')
    except Exception:
        return value


@register.filter
def truncate_words_middle(value, num):
    """
    Truncates a string to 'num' words, showing the start and end with ellipsis in the middle if needed.
    Usage:  value = "lorem ipsum dolor sit amet consectetur adipiscing elit"
            {{ value|truncate_words_middle:6 }}

    Output "lorem ipsum dolor ... adipiscing elit"
    """
    try:
        num = int(num)
        words = str(value).split()

        if len(words) <= num:
            return value  # No truncation needed

        half = num // 2
        start = words[:half] #first half
        end = words[-half:] if num % 2 == 0 else words[-(half + 1):] #second half accounting if the half is an odd number

        return ' '.join(start) + ' ... ' + ' '.join(end)

    except Exception:
        return value


@register.filter
def replace(value, args):
    """
    Replace old with new in string.
    Usage: {{ value|replace:"old,new" }}
    """
    try:
        old, new = args.split(',', 1)
        return str(value).replace(old, new)
    except Exception:
        return value

@register.filter
def startswith(value, text):
    """
    Check if string starts with text.
    Usage: {% if value|startswith:"Hello" %}
    """
    return str(value).startswith(str(text))

@register.filter
def endswith(value, text):
    """
    Check if string ends with text.
    Usage: {% if value|endswith:".jpg" %}
    """
    return str(value).endswith(str(text))

@register.filter
def slugify(value):
    """
    Slugify a string (for URLs).
    Usage: {{ value|slugify }}
    """
    return dj_slugify(value)

@register.filter
def strip_tags(value):
    """
    Remove HTML tags from string.
    Usage: {{ value|strip_tags }}
    """
    return dj_strip_tags(value)

@register.filter
def titlecase(value):
    """
    Convert string to title case.
    Usage: {{ value|titlecase }}
    """
    return str(value).title()

@register.filter
def lowercase(value):
    """
    Convert string to lowercase.
    Usage: {{ value|lowercase }}
    """
    return str(value).lower()

@register.filter
def uppercase(value):
    """
    Convert string to uppercase.
    Usage: {{ value|uppercase }}
    """
    return str(value).upper()


@register.filter
def remove(value, arg):
    """
    Remove all occurrences of arg from value.
    Usage: {{ value|remove:"foo" }}
    """
    return str(value).replace(str(arg), '')


@register.filter
def split(value, sep=','):
    """
    Split string by separator (default: comma).
    Usage: {% for tag in value|split:"," %}
    """
    return str(value).split(sep)


@register.filter
def join(value, sep=', '):
    """
    Join a list into a string with separator.
    Usage: {{ my_list|join:" / " }}
    """
    try:
        return sep.join(map(str, value))
    except Exception:
        return value
    

@register.filter
def center(value, args):
    """
    Center the string with args width and symbol.
    Usage: {{ value|center:"20,+" }}
    """
    try:
        width, symbol = args.split(',')
        return str(value).center(int(width), str(symbol))
    except Exception:
        return value


@register.filter(name='raw_text')
def raw_text(value):
    """ completely strip html tags and normalize whitespace (useful in richTextField) """
    if not value:
        return ''
    text = strip_tags(value)
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


@register.filter
def splitlines(value):
    """
    returns a list out of the string of characters broken by the \n
    """
    return value.splitlines()