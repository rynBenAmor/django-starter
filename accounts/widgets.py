# widgets.py
# ! ``template_name``: django quirk with the template path prefers an app directory 
# ! and will return a TemplateDoesNotExist if place elsewhere (yes even if you explicitly add one in 'DIRS')
# ! IT IS WHAT IT IS

from django import forms
import json
# ? ----------------------------------------------------------------
# ? end imports
# ? ----------------------------------------------------------------


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
    



class ColorPickerWidget(forms.TextInput):
    def __init__(self, attrs=None):
        default_attrs = {'type': 'color'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)