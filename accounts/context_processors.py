from .forms import LanguageTogglerForm
from django.utils.translation import get_language

def current_language_context(request):
    return {
        "language_form": LanguageTogglerForm(initial={'language': get_language()})
    }