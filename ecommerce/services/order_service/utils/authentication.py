import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class JWTUser:
    is_anonymous = False

    def __init__(self, payload):
        self.id               = payload.get("user_id")
        self.email            = payload.get("email", "")
        self.full_name        = payload.get("full_name", "")
        self.is_staff         = payload.get("is_staff", False)
        self.is_authenticated = True

    def __str__(self):
        return self.email


class MicroserviceJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth.startswith("Bearer "):
            return None
        token = auth.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, settings.JWT_SIGNING_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired.")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token.")
        return (JWTUser(payload), token)
