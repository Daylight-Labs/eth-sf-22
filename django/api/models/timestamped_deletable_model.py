from django.db import models
from django.utils import timezone
from datetime import datetime

from api.model_managers.deleted_objects_manager import ExcludeDeletedObjectsModelManager


class TimestampedDeletableModel(models.Model):
    """
    Base model class to be used in all models. 
    Adds created_on, last_modified, and deleted to all models.
    By default, objects will be filtered for non-soft deleted objects.
    """
    created_on = models.DateTimeField(auto_now_add=True)
    last_modified_on = models.DateTimeField(auto_now=True)
    deleted_on = models.DateTimeField(null=True, blank=True)

    objects = ExcludeDeletedObjectsModelManager()
    all_objects = models.Manager() # The default manager which includes deleted objects

    def delete(self, hard=False):
        if hard:
            super().delete()
        else:
            self.deleted_on = datetime.now()
            self.save()
    
    class Meta:
        ordering = ["id"]
        abstract = True