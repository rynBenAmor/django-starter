from .fields import HoneyPotField
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
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
          ! HoneyPotMixin must be referenced first
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


class UnsavedFormWarningMixin:
    """
    Adds a reusable unsaved-form warning for one HTML form.
    Usage: place UnsavedFormWarningMixin inside your form class, and include {{ form.unsaved_form_warning_script|safe }} in your template.
    Customize the warning message with `unsaved_warning_message` attribute or override `get_unsaved_warning_message()`.
     - Optionally specify a form ID with `unsaved_form_warning_form_id` if you have multiple forms on the page (otherwise it will target the closest form).
     - The script will automatically detect changes to form fields and prompt the user if they try to navigate away with unsaved changes. It also resets the warning state on form submission or reset.
    
    """

    unsaved_warning_message = _("You have unsaved changes. Are you sure you want to leave?")
    unsaved_form_warning_enabled = True
    unsaved_form_warning_form_id = None

    def __init__(self, *args, **kwargs):
        self.unsaved_form_warning_form_id = kwargs.pop('unsaved_form_warning_form_id', None)
        super().__init__(*args, **kwargs)

    @property
    def unsaved_form_warning_script(self):
        if not self.unsaved_form_warning_enabled:
            return ''

        message = str(self.unsaved_warning_message).replace("'", "\\'").replace("\n", ' ')

        if self.unsaved_form_warning_form_id:
            form_lookup = f"document.querySelector('#{self.unsaved_form_warning_form_id}')"
        else:
            form_lookup = 'document.currentScript.closest("form")'

        return mark_safe(f"""
            <script>
            (function() {{
                const form = {form_lookup};
                if (!form) return;

                const initialData = new FormData(form);
                let isDirty = false;

                const checkDirty = () => {{
                    const currentData = new FormData(form);
                    const keys = new Set();

                    for (const [key] of initialData) keys.add(key);
                    for (const [key] of currentData) keys.add(key);

                    for (const key of keys) {{
                        const initialValues = initialData.getAll(key);
                        const currentValues = currentData.getAll(key);

                        if (initialValues.length !== currentValues.length) {{
                            isDirty = true;
                            return;
                        }}

                        for (let i = 0; i < initialValues.length; i++) {{
                            if (initialValues[i] !== currentValues[i]) {{
                                isDirty = true;
                                return;
                            }}
                        }}
                    }}

                    isDirty = false;
                }};

                form.addEventListener('input', checkDirty);
                form.addEventListener('change', checkDirty);
                form.addEventListener('reset', () => {{
                    setTimeout(() => {{ isDirty = false; }}, 0);
                }});

                form.addEventListener('submit', () => {{ isDirty = false; }});

                window.addEventListener('beforeunload', (event) => {{
                    if (!isDirty) return;
                    event.preventDefault();
                    event.returnValue = '{message}';
                    return '{message}';
                }});
            }})();
            </script>
            """)

    def __str__(self):
        return mark_safe(super().__str__() + self.unsaved_form_warning_script)


# *=================================================================
# * CBV mixins
# *=================================================================

class FormMessageMixin:
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
