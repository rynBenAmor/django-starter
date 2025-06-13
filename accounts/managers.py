from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    """overriding CREATESUPERUSER since now authentication is done using email instead of username."""

    def create_superuser(self, email, password=None, **extra_fields):
        """Creates and saves a superuser with the given email and password."""
        if not email:
            raise ValueError("The Email field must be set")

        extra_fields.update({"is_staff": True, "is_superuser": True})
        
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user