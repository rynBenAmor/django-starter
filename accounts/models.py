from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
# Create your models here.


class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True, blank=False)

    is_email_verified = models.BooleanField(default=False)#on first signup

    #optional 2fa
    enabled_2fa = models.BooleanField(default=False)#can enable this through profile lets say
    is_2fa_authenticated = models.BooleanField(default=False)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email' #for authentication

    objects = CustomUserManager()  # Use the custom manager to skip username field in createsuperuser

    def __str__(self):
        return self.email


    def save(self, *args, **kwargs):
        self.email = self.email.lower().strip() #normalize email
        super().save(*args, **kwargs)
    
    @property
    def check_2fa_condition(self):
        if not self.enabled_2fa:
            return True  # No 2FA? You're good

        elif self.enabled_2fa and self.is_2fa_authenticated:
            return True  # 2FA enabled and already passed? You're good

        return False  # 2FA enabled but not passed? Block
    
    @property
    def check_if_email_verified(self):
        return self.is_email_verified or self.is_staff


        

