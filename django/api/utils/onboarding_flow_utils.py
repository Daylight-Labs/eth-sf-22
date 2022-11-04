
from api.models import OnboardingFlowCreationObject

def get_or_create_ftux_onboarding_obj(user):
    obj = OnboardingFlowCreationObject.objects.filter(creator=user).first()

    if obj is None:
        return OnboardingFlowCreationObject.objects.create(creator=user)

    return obj

def get_or_create_new_onboarding_obj(user):
    obj = OnboardingFlowCreationObject.objects.filter(flow__isnull=True, creator=user).first()

    if obj is None:
        return OnboardingFlowCreationObject.objects.create(creator=user)

    return obj