from django import template
register = template.Library()

@register.filter
def dict_get(d, key):
    """Safely get a value from a dict by key in templates."""
    if isinstance(d, dict):
        return d.get(key)
    return None

@register.filter
def dict_keys_list(d):
    """Return the keys of a dict as a list in templates."""
    if isinstance(d, dict):
        return list(d.keys())
    return []

@register.filter
def dict_values_list(d):
    """Return the values of a dict as a list in templates."""
    if isinstance(d, dict):
        return list(d.values())
    return []


@register.filter
def dict_is_empty(d):
    return not bool(d)

@register.filter
def dict_sum(d, key=None):
    """Sum all values or nested key in dict values."""
    if not isinstance(d, dict):
        return 0
    total = 0
    for v in d.values():
        if key and isinstance(v, dict):
            total += float(v.get(key, 0))
        else:
            total += float(v)
    return total
