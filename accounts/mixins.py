from .fields import HoneyPotField
from django.contrib import messages
# ? ----------------------------------------------------------------
# ? end imports
# ? ----------------------------------------------------------------


# *=================================================================
# * Field mixins
# *=================================================================

class HoneyPotMixin:
    """
    Automatically adds a honeypot field to any form using this mixin.
    Usage:
        class MyForm(HoneyPotMixin, forms.Form):
            name = forms.CharField()
    Note: no validation needed here since clean() exists in HoneyPotField()
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['honeypot'] = HoneyPotField()


class DisableAutocompleteMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['autocomplete'] = 'off'


class BootstrapFormMixin:
    """
    A very quick way to style a form with Bootstrap classes.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget_type = field.widget.__class__.__name__.lower()
            existing_classes = field.widget.attrs.get('class', '')

            if widget_type == 'select':
                field.widget.attrs['class'] = f"{existing_classes} form-select border-secondary w-100".strip()
            elif widget_type in ['textinput', 'textarea']:
                field.widget.attrs['class'] = f"{existing_classes} form-control w-100".strip()


class ReadOnlyFieldsMixin:
    """
    - Description : make specific form fields readonly
    - Usage : 
            class MyForm(ReadOnlyFieldsMixin, forms.ModelForm):
                readonly_fields = ['email']
    """
    readonly_fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.readonly_fields:
            if name in self.fields:
                self.fields[name].disabled = True


class OptionalFieldsMixin:
    """
    - Description : make specific form fields optional (useful in ModelForm)
    - Usage : 
            class MyForm(OptionalFieldsMixin, forms.ModelForm):
                optional_fields = ['email']
    """
    optional_fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.optional_fields:
            if name in self.fields:
                self.fields[name].required = False


class LowerTrimInputMixin:
    def clean(self, value):
        value = super().clean(value)
        if isinstance(value, str):
            value = value.lower().strip()
        return value

# *=================================================================
# * CBV mixins
# *=================================================================

class FlexibleFormMessageMixin:
    """
    Adds a customizable success message after form submission.

    - Use in class-based views like FormView, CreateView, or UpdateView.
    - Customize with `success_message` and `success_message_level` class attributes.
    - Override `get_success_message(cleaned_data)` for dynamic content.
    - Override `get_success_message_level()` for dynamic message type.

    Example:
        class MyView(FlexibleFormMessageMixin, CreateView):
            success_message = "User {username} created successfully!"
            success_message_level = messages.INFO

            def get_success_message(self, cleaned_data):
                return f"Welcome, {cleaned_data['username']}!"
    """
    success_message = "Form submitted successfully."
    success_message_level = messages.SUCCESS

    def get_success_message(self, cleaned_data):
        return self.success_message.format(**cleaned_data, object=getattr(self, 'object', None))

    def get_success_message_level(self):
        return self.success_message_level

    def form_valid(self, form):
        response = super().form_valid(form)
        message = self.get_success_message(form.cleaned_data)
        if message:
            messages.add_message(self.request, self.get_success_message_level(), message)
        return response
