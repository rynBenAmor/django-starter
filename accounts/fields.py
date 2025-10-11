
import json
from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .widgets import KeyValueWidget, ColorPickerWidget
import logging

logger = logging.getLogger(__name__)
# ? ----------------------------------------------------------------
# ? end imports
# ? ----------------------------------------------------------------


class HoneyPotField(forms.CharField):
    """
    A field to catch bots. Add to any form.
    Usage:
        class MyForm(forms.Form):
            honeypot = HoneyPotField()
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('required', False)
        kwargs.setdefault('label', '')
        kwargs.setdefault('widget', forms.TextInput(attrs={
            'style': 'height:0 !important;width:0 !important;opacity:0 !important;visibility:hidden !important;position:absolute !important;left:-9999px !important;z-index:-99999 !important;',
            'autocomplete': 'off',
            'tabindex': '-1',
        }))
        super().__init__(*args, **kwargs)

    def clean(self, value):
        value = super().clean(value)
        if value:
            logger.warning(f"Honeypot triggered with value: {value}")
            raise forms.ValidationError("Honeypot Spam detected", code='honeypot')
        return value




class JSONKeyValueField(forms.Field):
    """
    Description: i needed a way to add cleaning and validation logic, else can use KeyValueWidget + in-model cleaning
    Usage:
        from accounts.widgets import JSONKeyValueField

        class MyForm(forms.Form):
            my_json_field = JSONKeyValueField()
    """
    widget = KeyValueWidget()

    def validate(self, value):
        super().validate(value)
        if not isinstance(value, dict):
            raise ValidationError("Must be a JSON object (key-value pairs).")
        if not any(k.strip() and str(v).strip() for k, v in value.items()):
            raise ValidationError("At least one valid key-value pair is required.")

    def to_python(self, value):
        if value is None:
            return {}
        if isinstance(value, dict):
            data = value
        else:
            try:
                data = json.loads(value)
            except json.JSONDecodeError:
                raise ValidationError("Invalid JSON format.")
        cleaned = {}
        for k, v in data.items():
            if not k.strip():
                continue
            if v not in (None, "", []) and str(v).strip():
                cleaned[k.strip()] = v
        return cleaned



class ColorField(forms.CharField):
    """
    Usage: theme_color = ColorField(label="Choose Theme Color", initial="#ff0000")
    """
    default_validators = [
        RegexValidator(
            regex=r'^#(?:[0-9a-fA-F]{3}){1,2}$',
            message="Enter a valid hex color (e.g. #ff0000)."
        )
    ]

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', ColorPickerWidget)
        super().__init__(*args, **kwargs)