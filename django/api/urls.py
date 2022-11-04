from django.contrib import admin
from django.urls import path

from api.views import ping
from api.views.endpoints import get_referral_link, track_referral_link_signup, create_link, get_program_state,\
    track_referral_link_completion

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/ping', ping),
    path('api/referral_link/<str:link>', get_referral_link, name='get_referral_link'),
    path('api/referral_link/<str:link>/track_signup', track_referral_link_signup, name='track_referral_link_signup'),
    path('api/referral_link/<str:link>/track_completion', track_referral_link_completion, name='track_referral_link_completion'),
    path('api/create_link', create_link, name='create_link'),
    path('api/get_program_state', get_program_state, name='get_program_state')
]