from django import template
from django.utils.safestring import SafeString


register = template.Library()



@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Adds a CSS class to form fields.
    Usage : {{form.somefield|add_class:"form-control w-25 border-black"}}
    """
    if hasattr(field, 'as_widget'):  # If it's a form field
        return field.as_widget(attrs={"class": css_class})
    return field  # Return unchanged if not a form field



@register.simple_tag
def render_label(bound_field, css_class):
    """
    Renders a label with a custom CSS class, handling potential errors gracefully.
    Usage : {% render_label form.name "display-1 text-danger form-label" %}
    Note : this filter renders the field immediately via as_widget() like `|add_class`, order matters !
    """
    try:
        if bound_field and hasattr(bound_field, 'label_tag'):
            return bound_field.label_tag(attrs={'class': css_class})
        return ""  # Return an empty string if the field is None or invalid
    except Exception:
        pass



@register.filter(name='widget_type')
def widget_type(field):
    """
    Returns the widget type for the given form field
    Usage: ``{{ field|widget_type }}``
    """
    if hasattr(field, 'field'):
        field = field.field
    widget = field.widget
    return widget.__class__.__name__.lower()





@register.filter(name='add_attr')
def add_attr(field, attributes):
    """
    Adds HTML attributes to a form field widget.
    Usage: ``{{ field|attr:"class:form-control,data-toggle:tooltip" }}``
    Note : it must be used directly on the unrendered, meaning before custom filters like |add_class
    """
    if not field or not attributes:
        return field
    
    # Handle both BoundField and regular fields
    if isinstance(field, SafeString):
        # Already rendered field - can't modify attributes
        return field
        
    if not hasattr(field, 'field'):
        return field
    
    attrs = {}
    for attr_pair in attributes.split(','):
        if ':' in attr_pair:
            key, value = attr_pair.split(':', 1)
            attrs[key.strip()] = value.strip()
    
    widget = field.field.widget
    
    # Handle class attribute specially to append rather than replace
    if 'class' in attrs:
        if 'class' in widget.attrs:
            widget.attrs['class'] += ' ' + attrs['class']
        else:
            widget.attrs['class'] = attrs['class']
        del attrs['class']
    
    widget.attrs.update(attrs)
    return field




@register.filter(name="get_attr")
def get_attr(obj, attr):

    """important filter MUST not have the same name as a built in python function else it will loop and crash"""
    return getattr(obj, attr, None)




@register.filter(name="has_attr")
def has_attr(obj, attr) -> bool:
    """
    Note: important filter MUST not have the same name as a built in python function else it will loop and crash
    Usage: a more graceful way to check fields (especially fk), returns True or False
    Example: {{user|has_attr:"client_profile"}} 
    """
    return hasattr(obj, attr)


@register.filter
def batch(iterable, n=1):
    """
    Split an iterable into chunks of size n.
    Usage in template:
        ``  
        {% for chunk in my_list|batch:3 %}
            {% for object in chunk %}
            {% endfor %}
        {% endfor %}
        ``
    """
    length = len(iterable)
    n = int(n)
    for ndx in range(0, length, n):
        yield iterable[ndx:min(ndx + n, length)]
