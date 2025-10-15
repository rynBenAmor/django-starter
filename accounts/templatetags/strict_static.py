from django import template
from django.templatetags.static import static as django_static
from django.contrib.staticfiles import finders
from django.conf import settings
from urllib.parse import urljoin
import os

register = template.Library()

@register.simple_tag
def strict_static(path, absolute=False):
    """
    Stricter {% static %} that ensures existence of the file in DEBUG mode.
    Falls back to STATIC_ROOT if finders can't locate it.
    """
    url = django_static(path)

    if settings.DEBUG:
        resolved = finders.find(path)

        # Try static root as fallback
        if not resolved and settings.STATIC_ROOT:
            candidate = os.path.join(settings.STATIC_ROOT, path)
            if os.path.exists(candidate):
                resolved = candidate

        if not resolved or not os.path.exists(resolved):
            raise FileNotFoundError(f"Static file not found: '{path}'")

    if absolute:
        domain = getattr(settings, "SITE_DOMAIN_PREFIX", None)
        if domain:
            url = urljoin(domain, url)

    return url
