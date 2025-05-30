# widgets.py
from django import forms
import json
from django.core.exceptions import ValidationError


# a solution to make json fields more user-friendly
class KeyValueWidget(forms.Widget):
    """
    Description: a widget for displaying key-value pairs in a form for models.JSONField

    Usage:
        from accounts.widgets import KeyValueWidget
        from django import forms

        class MyForm(forms.ModelForm):
            class Meta:
                fields = ['my_json_field']
                model = MyModel
                my_json_field = forms.CharField( widget=KeyValueWidget() ) # or json.JSONField(widget=KeyValueWidget())
    """
    template_name = 'widgets/key_value_widget.html'

    def value_from_datadict(self, data, files, name):
        keys = data.getlist(f'{name}_key')
        values = data.getlist(f'{name}_value')
        return json.dumps(dict(zip(keys, values)))

    def format_value(self, value):
        if value is None:
            return []
        if isinstance(value, str):
            value = json.loads(value)
        return value.items()


        



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
    


from django import forms
from django.utils.safestring import mark_safe

class PDFPreviewWidget(forms.ClearableFileInput):
    """
    A FileInput widget that shows a PDF preview if a file is already uploaded.
    Usage:
        class MyForm(forms.ModelForm):
            class Meta:
                model = MyModel
                fields = ['my_pdf']
                widgets = {'my_pdf': PDFPreviewWidget}
    """
    template_name = 'widgets/pdf_preview_widget.html'

    def format_value(self, value):
        # value is a FieldFile or None
        return value

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['pdf_url'] = value.url if value and hasattr(value, 'url') else None
        return context