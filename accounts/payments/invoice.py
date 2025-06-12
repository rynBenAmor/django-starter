#pip install weasyprint
#download https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases 
# or sudo apt install libpangocairo-1.0-0 libcairo2 libgdk-pixbuf2.0-0 libffi-dev
from django.template.loader import get_template
from django.http import HttpResponse
import weasyprint


def render_pdf_from_template(request, template_name, context, filename="document.pdf"):
    """
    Renders a PDF from an HTML template using WeasyPrint.

    Args:
        request: Django request object (used to build absolute URIs).
        template_name (str): Path to the Django template file (relative to 'templates/' of course).
        context (dict): Context to render into the template.
        filename (str): The filename for the generated PDF (default: 'document.pdf').

    Returns:
        HttpResponse: A response object containing the generated PDF.
    
    Usage: 
        - in a view: return render_pdf_from_template(request, template_name='invoiceTest.html',  context=context, filename=f"invoice_{product.id}.pdf")
    Note: You can render any template to PDF, not just invoices, but it fits the theme of this module.
    """

    # Add domain to context for absolute image URLs
    context['domain'] = request.build_absolute_uri('/')[:-1]

    template = get_template(template_name)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="{filename}"'

    weasyprint.HTML(string=html).write_pdf(response)
    return response
