from django.db import models
from api.models.timestamped_deletable_model import TimestampedDeletableModel

class ReferralProgram(TimestampedDeletableModel):
    name = models.TextField()
    description = models.TextField()

    def __str__(self):
        return f"{self.name} - {self.description}"