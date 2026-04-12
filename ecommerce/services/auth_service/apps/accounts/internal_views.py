"""
Called by other services to fetch user info without hitting the public API.
Protected by X-Service-Token header.
"""
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer

User = get_user_model()

INTERNAL_TOKEN = getattr(settings, "INTERNAL_SERVICE_TOKEN", "")


def _verify_service_token(request):
    token = request.headers.get("X-Service-Token", "")
    if not token or token != INTERNAL_TOKEN:
        raise PermissionDenied("Invalid service token.")


class InternalUserDetailView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, pk):
        _verify_service_token(request)
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(UserSerializer(user).data)
