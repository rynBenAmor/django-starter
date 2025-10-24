import time
import logging
from functools import wraps

from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseBadRequest, HttpResponseForbidden
from django.db import transaction


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