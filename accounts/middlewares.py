# middleware/email_verification.py
from django.shortcuts import redirect
from django.urls import resolve
from django.contrib import messages
from django.contrib.auth import logout
from django.utils.translation import gettext_lazy as _




class EmailVerificationMiddleware:
    """check in every request is regular users are email verified"""
    def __init__(self, get_response):
        self.get_response = get_response

        # URLs you don’t want to block (login, signup, email confirmation, etc.)
        self.exempt_url_names = {

        }

    def __call__(self, request):
        user = request.user

        if user.is_authenticated and not user.is_staff:
            if not getattr(user, 'email_verified', False):
                current_url_name = resolve(request.path_info).url_name
                if current_url_name not in self.exempt_url_names:
                    logout(request)
                    messages.error(request, _("You must verify your email to continue."))
                    return redirect('accounts:login')

        return self.get_response(request)
