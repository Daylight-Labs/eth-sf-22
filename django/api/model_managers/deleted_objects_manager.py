from django.db import models

class ExcludeDeletedObjectsModelManager(models.Manager):
    """
    Only exposes objects that have NOT been soft-deleted.
    """
    def get_queryset(self):
        return super().get_queryset().filter(deleted_on__isnull=True)

    def with_deleted(self):
        return super().get_queryset()