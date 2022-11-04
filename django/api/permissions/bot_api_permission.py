from rest_framework import permissions

import os

API_CHATBOT_AUTH_TOKEN = os.environ['CHATBOT_API_AUTH_TOKEN']

class BotApiPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        auth_token = request.META.get('HTTP_AUTH')
        return auth_token == API_CHATBOT_AUTH_TOKEN

    def has_object_permission(self, request, view, obj):
        auth_token = request.META.get('HTTP_AUTH')
        return auth_token == API_CHATBOT_AUTH_TOKEN
