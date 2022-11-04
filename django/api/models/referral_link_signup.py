from django.db import models
from api.models.timestamped_deletable_model import TimestampedDeletableModel

class ReferralLinkSignup(TimestampedDeletableModel):
    referral_link = models.ForeignKey("ReferralLink", on_delete=models.CASCADE, related_name="link_signups")
    wallet = models.TextField()

    amount_deposited = models.IntegerField(null=True, blank=True)
    action_completed_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.wallet} --- {self.referral_link} --- {self.amount_deposited} --- {'COMPLETED' if self.action_completed_on else ''}"