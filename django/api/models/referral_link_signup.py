from django.db import models
from api.models.timestamped_deletable_model import TimestampedDeletableModel

class ReferralLinkSignup(TimestampedDeletableModel):
    referral_link = models.ForeignKey("ReferralLink", on_delete=models.CASCADE, related_name="link_signups")
    wallet = models.TextField()

    amount_deposited = models.DecimalField(null=True, max_digits = 10, decimal_places = 2)
    action_completed_on = models.DateTimeField(null=True, blank=True)
    first_deposit_date = models.DateTimeField(null=True, blank=True)
    twab = models.DecimalField(null=True, max_digits = 10, decimal_places = 2)
    reward_earned = models.DecimalField(null=True, max_digits = 10, decimal_places = 2)
    program_complete = models.BooleanField(null=True, default=False)

    def __str__(self):
        return f"{self.wallet} --- {self.referral_link} --- {self.amount_deposited} --- {'COMPLETED' if self.action_completed_on else ''}"