from api.models import ReferralLink, ReferralLinkSignup, ReferralProgram
from django.contrib import admin


class ReferralLinkAdmin(admin.ModelAdmin):
    class Meta:
        model = ReferralLink

admin.site.register(ReferralLink, ReferralLinkAdmin)

class ReferralLinkSignupAdmin(admin.ModelAdmin):
    class Meta:
        model = ReferralLinkSignup

admin.site.register(ReferralLinkSignup, ReferralLinkSignupAdmin)

class ReferralProgramAdmin(admin.ModelAdmin):
    class Meta:
        model = ReferralProgram

admin.site.register(ReferralProgram, ReferralProgramAdmin)