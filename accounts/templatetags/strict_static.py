from django import template
from django.templatetags.static import static as django_static
from django.conf import settings
import os

register = template.Library()

@register.simple_tag
def strict_static(path):
    """
    A stricter version of {% static %}:
    - In DEBUG mode, raises an error if file does not exist.
    - In production, behaves like normal {% static %}.
    """
    url = django_static(path)

    if settings.DEBUG:
        # resolve full local path
        from django.contrib.staticfiles.finders import find
        resolved = find(path)
        if not resolved or not os.path.exists(resolved):
            raise FileNotFoundError(f"Static file not found: '{path}'")

    return url
