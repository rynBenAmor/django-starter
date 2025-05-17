# accounts/middleware.py

from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import logout
from django.utils.translation import gettext_lazy as _




class Enforce2FAMiddleware:
    """check in every request is regular users are email verified"""
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
    Middleware that:
    restricts access to the admin panel, allowing only authenticated staff users.
    If maintenance mode 'name=maintenance' is active, it blocks all non-admin routes and makes '/admin/' publicly accessible    
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
       
        # If accessing /admin/, ensure only staff users can access
        if request.path.startswith('/admin/') and (not request.user.is_authenticated or not request.user.is_staff):
            return render(request, 'http_templates/404.html', status=404)  # Hides admin existence

        return self.get_response(request) #else let response be handled normally by the appropriate views



class AjaxOnlyMiddleware:
    """Middleware that verifies the presence of a custom header ``'X-Requested-With': 'MadeWithFetch'`` to ensure the request originates from JavaScript, preventing direct URL access."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/accounts/ajax/') and not request.headers.get('X-Requested-With') == 'MadeWithFetch':
            return render(request, 'http_templates/403_prohibited.html', status=403)

        return self.get_response(request)