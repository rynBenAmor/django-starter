
"""
    Auth Routes:
    ─────────────────────────────────────────────────────────────
    URL Name                        | Path (under /accounts/)
    ────────────────────────────────│────────────────────────────
    account_login                   | /accounts/login/
    account_logout                  | /accounts/logout/
    account_signup                  | /accounts/signup/

    Password Management:
    ─────────────────────────────────────────────────────────────
    account_reset_password          | /accounts/password/reset/
    account_reset_password_done     | /accounts/password/reset/done/
    account_reset_password_from_key | /accounts/password/reset/key/<uidb64>/<token>/
    account_reset_password_from_key_done | /accounts/password/reset/key/done/

    Email Management:
    ─────────────────────────────────────────────────────────────
    account_email                   | /accounts/email/
    account_email_verification_sent | /accounts/confirm-email/
    account_confirm_email           | /accounts/confirm-email/<key>/

    Social Accounts (if using social providers):
    ─────────────────────────────────────────────────────────────
    socialaccount_login_cancelled   | /accounts/social/login/cancelled/
    socialaccount_connections       | /accounts/social/connections/
    socialaccount_login_error       | /accounts/social/login/error/
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include



urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),#check source code

    path('', include('home.urls')),#can delete
]


handler400 = 'accounts.views.custom_400'
handler403 = 'accounts.views.custom_403'
handler404 = 'accounts.views.custom_404'
handler500 = 'accounts.views.custom_500'
handler429 = 'accounts.views.custom_403'

# Static & media for dev
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)