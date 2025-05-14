from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.urls import reverse
import time
from django.conf import settings
from django.utils.html import strip_tags



def send_verification_email(request, user):
    # Generate the default token
    token = default_token_generator.make_token(user)
    
    # Get the current timestamp (seconds since the epoch)
    timestamp = int(time.time())

    # Encode user ID and timestamp
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    # Prepare the URL with the timestamp included
    domain = get_current_site(request).domain
    link = f"https://{domain}{reverse('accounts:confirm_email', kwargs={'uidb64': uid, 'token': token, 'timestamp': timestamp})}"

    subject = 'Activer votre compte'
    html_message = render_to_string('registration/verify_your_email.html', {
        'user': user,
        'activation_link': link,
    })

    # Generate a plain text version of the email (for email clients that do not support HTML)
    plain_message = strip_tags(html_message)

    try:    
        #message is mandatory as a fallback plain text
        send_mail(subject,message=plain_message, html_message=html_message,  from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[user.email], fail_silently=True)

    except Exception:
        pass

