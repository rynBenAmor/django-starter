"""

**Future update for URL translation with i18n_patterns:**  
add the following in the main urls.py:  

    from django.conf.urls.i18n import i18n_patterns #possible url translation
    from django.utils.translation import gettext_lazy as _

    urlpatterns += i18n_patterns(
        path(_('accounts/'), include('accounts.urls', namespace='accounts')),
        prefix_default_language=True,
    )

Ensure all URLs use `gettext`, e.g., `path(_('login/'))`


"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView




urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),

    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),#can use nginx instead

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