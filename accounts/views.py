from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, resolve_url
from django.urls import reverse
from django.conf import settings
from django.utils.translation import activate
from .forms import *
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth import authenticate, login
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
import time
from django.conf import settings
from .utils import send_confirmation_email



def confirm_email(request, uidb64, token, timestamp):

    TOKEN_EXPIRATION_TIME = 86400  # 1 day

    try:
        uid = urlsafe_base64_decode(uidb64).decode()  # Decode the user ID
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        # Calculate token expiration
        current_timestamp = int(time.time())
        try:
            token_age = current_timestamp - int(timestamp)
        except ValueError:
            return render(request, "http_templates/410_invalid_token.html", status=410)

        if user.is_email_verified:
            messages.info(request, _("your account is already email verified ! it seems you have clicked an old verification link, you can connect directly") )
            return redirect("accounts:login")

        elif token_age <= TOKEN_EXPIRATION_TIME:
            user.is_email_verified = True
            user.save()
            messages.success(request, _("Success! you account is now up and ready to go"))

            return redirect("accounts:login")
        
        else:

            return render(
                request, "http_templates/410_invalid_token.html", status=410
            )
    # else
    return render(request, "http_templates/410_invalid_token.html", status=410)




def login_view(request):
    form = LoginForm(request.POST or None)  # GET requests get an empty form

    next_url = request.GET.get("next") or resolve_url("accounts:profile")  # Resolve URL name

    if not url_has_allowed_host_and_scheme(
        url=next_url, allowed_hosts={request.get_host()}
        ):
        next_url = reverse("accounts:profile")  # Fallback to a safe URL

    if request.method == "POST":
        if form.is_valid():
            email = form.cleaned_data.get("email").lower().strip()

            password = form.cleaned_data.get("password")

            user = authenticate(request, username=email, password=password)
            if user is not None:  

                if (user.is_staff) or (user.is_email_verified):
                    login(request, user)
                    return HttpResponseRedirect(resolve_url(next_url))
                
                else:
                    send_confirmation_email(request, user)#resend the email
                    messages.warning(request, _("make sure to check you email for a verification link, check your spam as well "))
                    return HttpResponseRedirect("accounts:login")

            elif user is None:
                # Handle invalid credentials
                form.add_error(None, _("invalid credentials "))
        else:
            messages.error(request, _("please correct the errors of the form"))

    context = {
        "form": form,
        "next": next_url,
    }
    return render(request, "registration/login.html", context)





def logout_view(request):
    logout(request)
    return redirect('accounts:login')  # or any other named URL or path


@login_required
def profile_view(request):
    return render(request, "registration/profile.html", {"user": request.user})


def set_language(request):
    if request.method == 'POST':
        form = LanguageTogglerForm(request.POST)
        if form.is_valid():
            language = form.cleaned_data['language']
            activate(language)# exp: activate('fr')
            response = redirect(request.META.get('HTTP_REFERER', '/'))
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)#defaults to 'django_language', auto checks when locale middleware exists
            print(settings.LANGUAGE_COOKIE_NAME)
            return response
    return redirect('/')


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


