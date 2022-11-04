from django.db import models
from api.models.timestamped_deletable_model import TimestampedDeletableModel

class ReferralLink(TimestampedDeletableModel):
    link = models.TextField()
    redirect_url = models.TextField()
    program = models.ForeignKey("ReferralProgram", on_delete=models.CASCADE, related_name="referral_links")

    def __str__(self):
        return f"Link {self.link} - {self.redirect_url}"