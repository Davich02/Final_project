from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        # массовое удаление
        return self.update(deleted_at=timezone.now())

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        # мягкое удаление
        return SoftDeleteQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)