from django.db import models
from django.utils import timezone
from .managers import SoftDeleteModelManager

class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteModelManager()

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save(using=using)

    def restore(self):
        self.deleted_at = None
        self.save()

    def hard_delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)

    class Meta:
        abstract = True
