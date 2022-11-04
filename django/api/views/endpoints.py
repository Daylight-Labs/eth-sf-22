from rest_framework.decorators import api_view
from django.http.response import JsonResponse

from api.models.referral_link import ReferralLink
from api.models.referral_link_signup import ReferralLinkSignup
from api.models.referral_program import ReferralProgram

@api_view(['GET'])
def get_referral_link(request, link):
    ref_link = ReferralLink.objects.filter(link=link).first()

    if ref_link is None:
        return JsonResponse({}, status=404)

    signup = ReferralLinkSignup.objects.filter(
        referral_link=ref_link
    ).order_by('-created_on').first()

    return JsonResponse({ "id": ref_link.id, "link": ref_link.link, "redirect_url": ref_link.redirect_url,
                          "is_action_completed": signup.action_completed_on is not None if signup else False,
                          "referrer_wallet": "0x096b0EFC859607f3n642eJL443E244C85e",
                          "referral_wallet": signup.wallet if signup else None})

@api_view(['POST'])
def track_referral_link_signup(request, link):
    wallet = request.data['wallet']

    ref_link = ReferralLink.objects.filter(link=link).first()

    if not ReferralLinkSignup.objects.filter(
                referral_link=ref_link,
                wallet=wallet
            ).exists():
        ReferralLinkSignup.objects.create(
            referral_link=ref_link,
            wallet=wallet
        )

    return JsonResponse({ "success": True, "redirect_url": ref_link.redirect_url })

@api_view(['POST'])
def track_referral_link_completion(request, link):
    wallet = request.data['wallet']

    ref_link = ReferralLink.objects.filter(link=link).first()

    signup = ReferralLinkSignup.objects.filter(
        referral_link=ref_link,
        wallet=wallet
    ).order_by('-created_on').first()

    signup.amount_deposited = 100

    from datetime import datetime

    signup.action_completed_on = datetime.now()
    signup.save()

    return JsonResponse({"success": True, "redirect_url": ref_link.redirect_url})

@api_view(['POST'])
def create_link(request):

    for link in ReferralLink.all_objects.all():
        link.delete(hard=True)

    for signup in ReferralLinkSignup.all_objects.all():
        signup.delete(hard=True)

    ref_link = ReferralLink.objects.create(
        link="df56aAch",
        redirect_url="https://pooltogether.com/",
        program=ReferralProgram.objects.first()
    )

    return JsonResponse({ "success": True, "redirect_url": ref_link.redirect_url, "link": ref_link.link })

@api_view(['GET'])
def get_program_state(request):
    ref_link = ReferralLink.objects.first()

    actions_completed = []

    for signup in ReferralLinkSignup.objects.all():
        actions_completed.append({
            "wallet": signup.wallet,
            "first_deposit_date": signup.action_completed_on,
            "time_weighted_average_balance": "1 $USDC" if signup.action_completed_on else "-",
            "reward_earned": "2 $USDC" if signup.action_completed_on else "-"
        })

    if len(ReferralLinkSignup.objects.all()) > 0:
        # You can add some fake data here
        pass

    return JsonResponse({ "link_exists": ref_link is not None, "link": ref_link.link if ref_link else None, "actions_completed": actions_completed })