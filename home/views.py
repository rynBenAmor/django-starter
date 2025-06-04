from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def home_view(request):

    messages.success(request, 'success , lorem ipsm soemthi sdas auto der nacht')
    messages.error(request, 'error , lorem ipsm soemthi sdas auto der nacht')
    messages.warning(request, 'warning , lorem ipsm soemthi sdas auto der nacht')
    messages.info(request, 'info , lorem ipsm soemthi sdas auto der nacht')

    return render(request, "home/home.html")


