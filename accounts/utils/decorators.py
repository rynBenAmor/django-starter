import time
import logging
from functools import wraps
import re

from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseBadRequest, HttpResponseForbidden
from django.db import transaction
from functools import wraps
from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from typing import Dict, Callable, Any, Optional
from django.http import Http404

import logging

# Logger
logger = logging.getLogger(__name__)

# ?-----------------------------end imports-------------------

def not_authenticated_required(next_url):

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                return redirect(f"{next_url}")
            return view_func(request, *args, **kwargs)

        return _wrapped_view
    
    return decorator


def ajax_required(header_name="X-Requested-With", header_value="XMLHttpRequest"):
    """
    A decorator to ensure the request is an AJAX request.

    Args:
        header_value (str): The expected value of the header.
        header_name (str): The request header to check (default is 'x-requested-with').

    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.headers.get(header_name) != header_value:
                return HttpResponseBadRequest("AJAX request required.")
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def atomic_transaction(func=None):
    """
    Decorator ensures that all database operations inside the function either succeed together or fail together

    Works both with and without parentheses:

    Example:

        @atomic_transaction
        def transfer_funds(sender, receiver, amount):
            sender.balance -= amount
            sender.save()

            receiver.balance += amount
            receiver.save()

            if receiver.balance > 1_000_000:  # simulate error
                raise ValueError("Suspicious balance!")
    """
    def _decorator(f):
        @wraps(f)
        def _wrapped(*args, **kwargs):
            with transaction.atomic():
                return f(*args, **kwargs)
        return _wrapped

    if func is None:
        return _decorator
    return _decorator(func)


def retry_on_exception(times: int = 3, exceptions=(Exception,), delay_seconds: float = 0.5):
    """
    Decorator to retry a function call on transient exceptions with linear backoff.

    Args:
        times (int): Maximum number of attempts (default: 3).
        exceptions (tuple): Exception classes to catch (default: (Exception,)).
        delay_seconds (float): Base delay between retries in seconds.
            The actual wait time increases linearly: delay_seconds * attempt.

    Example:
        @retry_on_exception(times=3, exceptions=(IOError,))
        def some_view():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == times:
                        raise  # re-raise the last exception
                    time.sleep(delay_seconds * attempt)
        return wrapped
    return decorator


def staff_member_or_denied(status_code=404, redirect_url=None, log_attempts=False):
    """
    Decorator for views that checks if the user is authenticated and is a staff member.
    If not:
      - redirects to `redirect_url` if given,
      - or raises the specified status_code (404 by default),
      - optionally logs unauthorized access attempts.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated or not request.user.is_staff:
                if log_attempts:
                    logger.warning(
                        "Unauthorized access attempt by %s to %s",
                        request.user if request.user.is_authenticated else "anonymous",
                        request.path
                    )

                if redirect_url:
                    return redirect(redirect_url)

                match status_code:
                    case 403:
                        raise PermissionDenied
                    case 404:
                        raise Http404
                    case _:
                        return HttpResponseForbidden()

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


# ?-----------------------------HTMX partials decorator-------------------
class PartialConfig:
    """Configuration for partial decorator"""
    def __init__(
        self,
        partials: Dict[str, str],
        default: str = "deny",
        require_query: bool = True,
        full_template: Optional[str] = None,  # NEW: Template for full page
        ):
        self.partials = partials
        self.default = default
        self.require_query = require_query
        self.full_template = full_template  # Store the full page template


def handle_partials(config: PartialConfig):
    """
    HTMX Django 6 exclusive (django_htmx and middleware are required):
    Decorator to handle HTMX partial requests based on a configuration object. 
    It checks if the request is an HTMX request and if a valid partial name is provided. 
    Depending on the conditions, it renders the appropriate template or redirects as needed.
    example:
        my_partials = PartialConfig(
            partials={
                "message_list": "notifications/partials.html#message_list",
                "deny": "partials/ui.html#ui_deny_partial",
            },
            #full_template='home/home.html',  # optional Template for full page
        )

        @handle_partials(my_partials)
    """
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
            
            is_htmx = request.headers.get('HX-Request') == 'true'
            print(request.get_host() + request.path)
            
            # Explicit intent via query param
            partial_name = None
            if config.require_query:
                partial_name = request.GET.get("partial")
                if partial_name:
                    if not re.match(r'^[a-zA-Z0-9_-]+$', partial_name):
                        logger.warning(f"Invalid partial name attempted: {partial_name}")
                        return HttpResponse("Invalid request", status=400)
            
            # Get context data from view
            context = view_func(request, *args, **kwargs)
            
            if isinstance(context, HttpResponse):
                return context
            
            # Case 1: Valid HTMX partial request
            if is_htmx and partial_name:
                template = config.partials.get(partial_name, config.partials.get(config.default)) or ""
                return render(request, template, context)
            
            # Case 2: HTMX request but missing partial name
            if is_htmx and config.require_query and not partial_name:
                logger.info(f"HTMX request missing partial param: {request.path}")
                if config.default in config.partials:
                    return render(request, config.partials[config.default], context)
            
            # Case 3: Non-HTMX request with partial param (user typing URL)
            if partial_name and not is_htmx:
                # redirect to 404 page
                raise Http404
            
            # Case 4: Normal request - render full page
            if config.full_template:
                return render(request, config.full_template, context)
            
            # Fallback
            return HttpResponse("No template specified", status=500)
            
        return wrapper
    return decorator