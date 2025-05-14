from .forms import LanguageTogglerForm
from django.utils.translation import get_language

def current_language_context(request):
    context = {
        "language_form": LanguageTogglerForm(initial={'language': get_language(),}),
        "current_language_key": get_language(),
    }
    return context