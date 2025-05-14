from django.shortcuts import render
from django.conf import settings
from django.shortcuts import redirect
from django.utils.translation import activate
from .forms import LanguageTogglerForm


def set_language(request):
    if request.method == 'POST':
        form = LanguageTogglerForm(request.POST)
        if form.is_valid():
            language = form.cleaned_data['language']
            activate(language)
            response = redirect(request.META.get('HTTP_REFERER', '/'))
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
            return response
    return redirect('/')


def custom_404(request, *args, **kwargs):
    return render(request, "http_templates/404.html", status=404)


def custom_403(request, exception=None):

    return render(request, "http_templates/403_prohibited.html", status=403)

def csrf_failure(request, reason=""):
    #alternatively create a 403_csrf.html with template priority
    return render(request, "http_templates/403_prohibited.html", status=403)


def custom_400(request, *args, **kwargs):
    return render(request, "http_templates/400_bad_request.html", status=400)


def custom_500(request, *args, **kwargs):
    return render(request, "http_templates/500_internal_server_error.html", status=500)


