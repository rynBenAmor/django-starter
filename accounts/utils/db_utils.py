
import os
import uuid

from django.db import IntegrityError
from django.db.models.fields.files import FieldFile
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils.timezone import now

def model_to_full_dict(instance):
    """
    Returns a dict of all fields (including FileFields) for a model instance.
    """
    data = {}
    for field in instance._meta.get_fields():
        if hasattr(instance, field.name):
            value = getattr(instance, field.name)
            if isinstance(value, FieldFile):
                data[field.name] = value.url if value else None
            else:
                data[field.name] = value
    return data




def get_or_create_atomic(model, defaults=None, **kwargs):
    """
    Atomic get_or_create to avoid race conditions.
    """
    try:
        with transaction.atomic():
            return model.objects.get_or_create(defaults=defaults, **kwargs)
    except IntegrityError:
        return model.objects.get(**kwargs), False


def get_object_or_none(model, **kwargs):
    """
    Returns an object or None if not found.
    """
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None


def get_by_natural_key_or_404(model, *args):
    """
    Returns an object by natural key or raises 404.
    Note : in class Meta you must add natural_key_fields = ['name']

    """
    return get_object_or_404(model, **dict(zip(model.natural_key_fields, args)))




class GenerateUniqueFileName:
    """
    A callable class for Django's `upload_to` parameter that generates a unique file path
    for uploaded files, helping prevent filename conflicts and path length issues.

    Features:
    - Generates a short, UUID-based filename to avoid issues like `SuspiciousFileOperation`
    caused by overly long file names or unintended file overwrites.
    - Organizes uploaded files into subdirectories by year.
    - Preserves the original file extension.

    File Path Format:
        ``<base_folder>/<year>/<uuid>.<ext>``

    Example:
        ``
        image = models.ImageField(
            upload_to=GenerateUniqueFileName('product_images'),
            verbose_name="Main Product Image"
        )
        ``
        - **Note:** The `deconstruct()` method is required for Django to serialize callable objects (like this class) in migrations. Without it, `makemigrations` will fail.
        - ⚠️ Also, once this class is used in a migration, it's effectively "frozen" in that file. Deleting or renaming the class later — even if it's no longer used in your models — will break migrations unless you manually edit or fake them.

    """

    def __init__(self, base_folder):
        self.base_folder = base_folder

    def __call__(self, instance, filename):
        ext = os.path.splitext(filename)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        year = now().year
        return os.path.join(self.base_folder, str(year), unique_name)

    def deconstruct(self):
        """
        Tells Django how to serialize this callable for migrations.
        """
        # Return the full import path, no args/kwargs except the base_folder
        return (
            f"{self.__module__}.{self.__class__.__name__}",  # import path
            [self.base_folder],  # positional args
            {},  # keyword args
        )


