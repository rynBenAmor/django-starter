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
from django.core.signing import TimestampSigner
from django.core.mail import EmailMultiAlternatives
import random



def send_verification_email(request, user):
    # Generate the default token
    token = default_token_generator.make_token(user)
    
    # Get the current timestamp (seconds since the epoch)
    timestamp = int(time.time())
    signer = TimestampSigner() #cleaner than Signer in this use case
    signed_timestamp = signer.sign(str(timestamp))

    # Encode user ID and timestamp
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    # Prepare the URL with the timestamp included
    domain = get_current_site(request).domain
    link = f"https://{domain}{reverse('accounts:verify_email', kwargs={'uidb64': uid, 'token': token, 'signed_ts': signed_timestamp})}"

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








def send_2fa_code(request, user, subject="Your 2FA Code", message_template=None):
    """
    Generates a 4-digit 2FA code, stores session info, and sends it to the user's email.
    """

    code = str(random.randint(1000, 9999))
    request.session['2fa_user_id'] = user.id
    request.session['2fa_code'] = code
    request.session['2fa_created_at'] = int(time.time())

    message = message_template or f"Your 2FA code is: {code}"

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )




class EmailMATemplate:
    """
    - this is an efficient utility shortcut for creating EmailMultiAlternatives in case of 
        a for loop mailing on a single SMTP connection (instead of send_mail)
    - Usage: 

        from django.core.mail import get_connection

        connection = get_connection()  # Reuse the same SMTP connection
        connection.open()  # Explicitly open once for efficiency

        for user in users:
        
            EmailMATemplate(
                subject="Nouvel arrivage pour vous",
                template_path="emails/new_arrival_email.html", # relative to 'template/' path of course
                context={"user_name": user.get_full_name()},
                to=user.email
                connection=connection
            ).send()

        connection.close()

    """
    
    def __init__(self, subject:str, template_path:str, context:object = None, from_email:str = None, to:list = None, connection=None):
        
        if not to:
            raise ValueError("Recipient 'to' must be provided.")
        
        self.subject = subject
        self.template_path = template_path 
        self.context = context or {}
        self.from_email = from_email or settings.DEFAULT_FROM_EMAIL
        self.to = to if isinstance(to, list) else [to]
        self.connection = connection

    def send(self):
        html_body = render_to_string(self.template_path, self.context)
        text_body = strip_tags(html_body)
        
        email = EmailMultiAlternatives(
            subject=self.subject,
            body=text_body,
            from_email=self.from_email,
            to=self.to,
            connection=self.connection,
        )
        email.attach_alternative(html_body, "text/html")
        email.send()
        return email




from django.shortcuts import redirect
from functools import wraps

def not_authenticated_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('accounts:profile')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
