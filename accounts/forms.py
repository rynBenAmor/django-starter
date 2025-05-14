from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class LanguageTogglerForm(forms.Form):
    language = forms.ChoiceField(
        label=_("Select Language"),
        choices=settings.LANGUAGES,
        widget=forms.Select(attrs={'onchange': 'this.form.submit();'})
    )