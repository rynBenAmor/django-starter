from django.contrib.auth.models import BaseUserManager
from .querysets import SoftDeleteQuerySet
from django.db import models


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
    
    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a user with the given email and password."""
        if not email:
            raise ValueError("The Email field must be set")

        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    



class SoftDeleteModelManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).alive()

    def deleted(self):
        return SoftDeleteQuerySet(self.model, using=self._db).deleted()

    def all_with_deleted(self):
        return SoftDeleteQuerySet(self.model, using=self._db)
