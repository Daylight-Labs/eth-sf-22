from rest_framework.decorators import api_view
from django.http.response import JsonResponse


@api_view(['GET'])
def ping(request):
    return JsonResponse("pong", safe=False)