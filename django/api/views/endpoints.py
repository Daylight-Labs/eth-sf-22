from rest_framework.decorators import api_view
from django.http.response import JsonResponse

from api.models.referral_link import ReferralLink
from api.models.referral_link_signup import ReferralLinkSignup
from api.models.referral_program import ReferralProgram

from datetime import datetime

import requests
import time

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

    # TODO: For each referral signup
    # 1) Get first deposit into Pooltogether
    # 2) Calculate TWAB from then til now (stop at 30 days)
    # 3) Calcualte the rewards 

    signups = ReferralLinkSignup.objects.all()

    for s in signups:
        reload = False
        if s.twab is None or reload:
            url = f"https://api.etherscan.io/api?module=account&action=tokentx&address={s.wallet}&startblock=13259077&endblock=15888321&sort=asc&apikey=IFNIIPV2DX24MAPCWISG97527YQP59T85X&contractaddress=0xdd4d117723C257CEe402285D3aCF218E9A8236E1"
            response = requests.get(url)
            transactions = response.json()["result"]
            transactions.sort(key=get_timestamp)
            twab_table = make_twab_table(transactions, s.wallet)

            # TODO: handle case with only one deposit transaction
            
            first_time = twab_table[0]["time"]
            last_time = twab_table[-1]["time"]
            duration = (last_time - first_time)
            days = duration / 86400

            thirty_day_mark = first_time + (30 * 86400)
            
            end_of_reward_transaction_index = None
            for i, t in enumerate(transactions):
                if "is_reward_end" in t.keys():
                    end_of_reward_transaction_index = i
                    break

            avg_balance_raw = None
            if end_of_reward_transaction_index:
                avg_balance_raw = (twab_table[end_of_reward_transaction_index]["twab_amount"] - twab_table[0]["twab_amount"]) / (twab_table[end_of_reward_transaction_index]["time"] - twab_table[0]["time"])
            else:
                t = time.time()
                new_twab_amount = twab_table[-1]["twab_amount"] + twab_table[-1]["current_balance"] * (t - twab_table[-1]["time"])
                avg_balance_raw = (new_twab_amount - twab_table[0]["twab_amount"]) / (t - twab_table[0]["time"]) 

            avg_balance = avg_balance_raw * 10**-6

            first_deposit_date = datetime.utcfromtimestamp(first_time)

            s.first_deposit_date = first_deposit_date
            s.twab = avg_balance
            s.reward_earned = avg_balance * 0.05
            s.program_complete = not(end_of_reward_transaction_index is None)
            s.save()
        

        actions_completed.append({
            "wallet": s.wallet,
            "first_deposit_date": s.first_deposit_date,
            "time_weighted_average_balance": f"{s.twab}",
            "reward_earned": f"{s.reward_earned}",
            "program_complete": "Yes" if s.program_complete else "No"
        })

    if len(ReferralLinkSignup.objects.all()) > 0:
        # You can add some fake data here
        pass

    return JsonResponse({ "link_exists": ref_link is not None, "link": ref_link.link if ref_link else None, "actions_completed": actions_completed })

def get_timestamp(t):
  return t["timeStamp"]

def make_twab_table(transactions, wallet):
  twab_table = []
  last_twab_amount = 0
  last_twab_time = 0
  current_balance = 0
  current_time = 0

  thirty_day_mark = int(transactions[0]["timeStamp"]) + (30 * 86400)
  if int(transactions[-1]["timeStamp"]) > thirty_day_mark:
    transactions.append({
        "timeStamp": f"{thirty_day_mark}",
        "value":0,
        "to": "0x",
        "from": "0x",
        "is_reward_end": True
    })
    transactions.sort(key=get_timestamp)

  for transaction in transactions:
    current_time = int(transaction["timeStamp"])
    new_twab_amount = last_twab_amount + current_balance * (current_time - last_twab_time)

    current_balance = current_balance + convert_transaction_to_signed_amount(transaction, wallet)  
  
    twab_table.append({"time": current_time, "twab_amount":new_twab_amount, "current_balance": current_balance})
  
    last_twab_amount = new_twab_amount
    last_twab_time = current_time
  return twab_table

def convert_transaction_to_signed_amount(t, wallet):
  if t["to"] == wallet:
    return int(t["value"])
  else:
    return -int(t["value"])