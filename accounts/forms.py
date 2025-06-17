from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from .mixins import HoneyPotMixin
from .fields import ColorField
# ? ----------------------------------------------------------------
# ? end imports
# ? ----------------------------------------------------------------


class LanguageTogglerForm(forms.Form):
    language = forms.ChoiceField(
        label=_("Select Language"),
        choices=settings.LANGUAGES,
        widget=forms.Select(attrs={'onchange': 'this.form.submit();', 'title': 'language-toggler'})
    )



class LoginForm(HoneyPotMixin, forms.Form):

    email = forms.EmailField(max_length=255, required=True,
                             label=_("email"),
                             widget= forms.EmailInput(
                                 attrs={"placeholder": _("email")}
                             ))
    
    password = forms.CharField(
        label=_("password"),
        widget= forms.PasswordInput(
            attrs={
                "placeholder": _("password")
            }
        )
    )

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        return email.lower().strip()

