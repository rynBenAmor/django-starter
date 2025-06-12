#pip install weasyprint
#download https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases 
# or sudo apt install libpangocairo-1.0-0 libcairo2 libgdk-pixbuf2.0-0 libffi-dev
from django.template.loader import get_template
from django.http import HttpResponse
from django.core.files.base import ContentFile
import weasyprint

def render_pdf_from_template(request, template_name, context, filename="document.pdf", return_file=False):
    """
    Renders a PDF from an HTML template using WeasyPrint.

    Args:
        request: Django request object (used to build absolute URIs).
        template_name (str): Path to the Django template file.
        context (dict): Template context.
        filename (str): Name of the generated PDF file.
        return_file (bool): If True, returns a tuple (HttpResponse, ContentFile).

    Returns:
        HttpResponse | (HttpResponse, ContentFile): PDF response or tuple if return_file=True.

    Usage:
        response = render_pdf_from_template(request, 'invoice.html', context)
        return response
        # ? OR to also get the raw file:
        response, pdf_file = render_pdf_from_template(request, 'invoice.html', context, return_file=True)
        product.pdf.save(pdf_file.name, pdf_file, save=True)
        return response
    """
    context['domain'] = request.build_absolute_uri('/')[:-1]
    template = get_template(template_name)
    html = template.render(context)

    # Generate PDF in memory
    pdf_bytes = weasyprint.HTML(string=html).write_pdf()

    # Build the HTTP response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="{filename}"'
    response.write(pdf_bytes)

    if return_file:
        return response, ContentFile(pdf_bytes, name=filename)
    return response
