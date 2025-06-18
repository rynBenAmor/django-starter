from django import template
import random


register = template.Library()


@register.filter
def batch(iterable, n=1):
    """
    Split an iterable into chunks of size n.
    Usage in template:
        ``  
        {% for chunk in my_list|batch:3 %}
            {% for object in chunk %}
            {% endfor %}
        {% endfor %}
        ``
    """
    length = len(iterable)
    n = int(n)
    for ndx in range(0, length, n):
        yield iterable[ndx:min(ndx + n, length)]


@register.filter
def slice_list(value, arg):
    """
    Slice a list or queryset: {{ my_list|slice_list:"start:end" }}
    Example: {{ my_list|slice_list:"0:5" }}
    """
    try:
        start, end = (int(x) if x else None for x in arg.split(':'))
        return value[start:end]
    except Exception:
        return value




@register.filter
def shuffle(value):
    """
    Shuffle a list or queryset randomly.
    Usage: {{ my_list|shuffle }}
    """
    try:
        result = list(value)
        random.shuffle(result)
        return result
    except Exception:
        return value


@register.filter
def unique(value):
    """
    Return unique items from a list or queryset.
    Usage: {{ my_list|unique }}
    """
    try:
        return list(dict.fromkeys(value))
    except Exception:
        return value





@register.filter
def length_gt(value, n):
    """
    Returns True if length of value > n.
    Usage: {% if my_list|length_gt:3 %}
    """
    try:
        return len(value) > int(n)
    except Exception:
        return False

@register.filter
def length_lt(value, n):
    """
    Returns True if length of value < n.
    Usage: {% if my_list|length_lt:3 %}
    """
    try:
        return len(value) < int(n)
    except Exception:
        return False


@register.filter
def first(value):
    """
    Return the first item of a list/queryset.
    Usage: {{ my_list|first }}
    """
    try:
        return value[0]
    except Exception:
        return None

@register.filter
def last(value):
    """
    Return the last item of a list/queryset.
    Usage: {{ my_list|last }}
    """
    try:
        return value[-1]
    except Exception:
        return None

@register.filter
def dictsort(value, key):
    """
    Sort a list of dicts by a key.
    Usage: {{ my_list|dictsort:"name" }}
    """
    try:
        return sorted(value, key=lambda x: x.get(key))
    except Exception:
        return value

@register.simple_tag
def paginate(value, page, per_page):
    """
    Paginate a list: {% paginate my_list page per_page as page_obj %}
    """
    try:
        page = int(page)
        per_page = int(per_page)
        start = (page - 1) * per_page
        end = start + per_page
        return value[start:end]
    except Exception:
        return value


@register.filter
def pluck(queryset, attr):
    """
    Extract a single attribute from each item in a list/queryset as a list
    Usage: {{ my_list|pluck:"name" }}    
    """
    try:
        return [getattr(item, attr, None) for item in queryset]
    except Exception:
        return queryset
    

@register.filter
def exclude_none(values):
    """loops through an iterable and returns a list without None items"""
    return [v for v in values if v is not None]

@register.filter
def list_queryset(value):
    """coerce the queryset into a list"""
    return list(value)  # Forces evaluation