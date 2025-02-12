from django.conf import settings
from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication


class TokenExpireAuthentication(TokenAuthentication):
    def authenticate(self, request):
        try:
            user, token = super().authenticate(request=request)
        except exceptions.AuthenticationFailed as e:
            raise exceptions.AuthenticationFailed(e)
        except TypeError:
            return None
        else:
            if (timezone.now() - token.created).seconds > settings.TOKEN_EXPIRE_SECONDS:
                token.delete()
                raise exceptions.AuthenticationFailed("Token expired")
            return user, token
