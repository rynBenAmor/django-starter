from django.shortcuts import render

# Create your views here.

def custom_404(request, *args, **kwargs):
    return render(request, "http_templates/404.html", status=404)


def custom_403(request, exception=None):

    return render(request, "http_templates/403_prohibited.html", status=403)

def csrf_failure(request, reason=""):
    #alternatively create a 403_csrf.html with template priority
    return render(request, "http_templates/403_prohibited.html", status=403)


def custom_400(request, *args, **kwargs):
    return render(request, "http_templates/400_bad_request.html", status=400)


def custom_500(request, *args, **kwargs):
    return render(request, "http_templates/500_internal_server_error.html", status=500)


