
import ipaddress
import uuid
from django.core.cache import cache
from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import redirect
from django.conf import settings
from django.http import HttpRequest

# * ==========================================================
# * URLS and api
# * ==========================================================


def request_rate_limit(
    request, key: str, limit: int = 5, time_window: int = 60
    ) -> bool:
    """
    Limits the number of requests per user or session for a given key within a time window.

    Args:
        request: Django request object.
        key (str): Identifier for the type of action (e.g., "login").
        limit (int): Number of allowed requests.
        window (int): Time window in seconds.

    Returns:
        bool: True if allowed, False if rate-limited.
    """
    if request.user.is_authenticated:
        identifier = str(request.user.pk)
    else:
        # Ensure session exists (creates one if using cookie-based sessions)
        session_key = request.session.session_key
        if not session_key:
            try:
                request.session.save()
            except Exception:
                # Fallback to a per-process identifier if sessions cannot be created
                session_key = None
        identifier = session_key or uuid.uuid4().hex

    cache_key = f"rate_limit:{key}:{identifier}"
    count = cache.get(cache_key, 0)

    if count >= limit:
        return False

    if count == 0:
        # First request: set with expiration
        cache.set(cache_key, 1, timeout=time_window)
    else:
        # Increment without resetting TTL
        cache.incr(cache_key)

    return True




def safe_redirect(request, url, fallback_url="/"):
    """
    Redirects to a URL only if it's considered safe, otherwise falls back.

    - Uses settings.ALLOWED_HOSTS for global safety.
    - Accepts both relative URLs and absolute URLs to allowed hosts.
    - Prevents open redirect vulnerabilities.
    """
    if url and url_has_allowed_host_and_scheme(
        url=url,
        allowed_hosts=settings.ALLOWED_HOSTS or None,  # None falls back to settings
        require_https=request.is_secure(),
    ):
        return redirect(url)
    return redirect(fallback_url)



def get_request_ip(request: HttpRequest) -> str:
    """
    Return the real client IP address, even behind a reverse proxy.
    """
    # Common headers set by proxies (order matters)
    headers_to_check = [
        'HTTP_X_FORWARDED_FOR',  # can be a list: client, proxy1, proxy2
        'HTTP_X_REAL_IP',        # often set by Nginx
        'REMOTE_ADDR',           # direct connection fallback
    ]

    for header in headers_to_check:
        ip = request.META.get(header)
        if ip:
            # If X-Forwarded-For has multiple IPs, take the first (the client)
            if header == 'HTTP_X_FORWARDED_FOR':
                ip = ip.split(',')[0].strip()
            return ip

    return ''


def is_ipv4_address(ip: str) -> bool:
    try:
        return isinstance(ipaddress.ip_address(ip), ipaddress.IPv4Address)
    except ValueError:
        return False


def is_ipv6_address(ip: str) -> bool:
    try:
        return isinstance(ipaddress.ip_address(ip), ipaddress.IPv6Address)
    except ValueError:
        return False


def is_public_ip(ip: str) -> bool:
    try:
        return ipaddress.ip_address(ip).is_global
    except ValueError:
        return False