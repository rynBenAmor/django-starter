# accounts/middleware.py

from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import logout
from django.utils.translation import gettext_lazy as _
import logging


logger = logging.getLogger(__name__)



class Enforce2FAMiddleware:
    """
    ? optional:
    check in every request is regular users are email verified through a custom property method
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        if user.is_authenticated:
            if not user.check_2fa_condition:
                    logout(request)
                    messages.error(request, _("You must verify with 2FA to continue. Please check your email for a verification code"))
                    return redirect('accounts:login')

        return self.get_response(request)



class AdminAccessMiddleware:
    """
    * Recommended:
    Restricts access to the admin panel to authenticated staff users only.
    Returns 404 for unauthorized access to hide admin existence.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        admin_url = reverse('admin:index')
        if request.path_info.startswith(admin_url):
            user = request.user
            if not user.is_authenticated or not user.is_staff:
                logger.critical("Unauthorized admin access attempt: IP=%s, Path=%s, User=%s",
                    request.META.get('REMOTE_ADDR'),
                    request.path_info,
                    user if user.is_authenticated else 'Anonymous'
                )
                return render(request, 'http_templates/404.html', status=404)
        return self.get_response(request)



class IPWhitelistMiddleware:
    """
    ? situational:
    Restricts access to specified paths (e.g., admin) to whitelisted IP addresses.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.WHITELISTED_IPS = {'127.0.0.1',}  # Add your trusted IPs here
        self.PROTECTED_PATHS = [reverse('admin:index').rstrip('/'), '/another-secret-path', ] # Add your to-be-protected paths here

    def __call__(self, request):
        client_ip = request.META.get('REMOTE_ADDR')
        for path in self.PROTECTED_PATHS:
            if request.path_info.startswith(path):
                if client_ip not in self.WHITELISTED_IPS:
                    logger.critical(
                        "Blocked non-whitelisted IP: IP=%s, Path=%s, User=%s",
                        client_ip, 
                        request.path_info,
                        request.user if request.user.is_authenticated else "Anonymous"
                    )
                    return render(request, 'http_templates/404.html', status=404)
        return self.get_response(request)