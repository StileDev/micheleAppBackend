"""
Les WebSockets ne peuvent pas envoyer d'en-tête Authorization comme une
requête HTTP classique. Le token JWT est donc passé en paramètre de
requête : ws://.../ws/parcelles/12/?token=<access_token>

Ce middleware lit ce paramètre, valide le token avec SimpleJWT, et place
l'utilisateur correspondant dans scope['user'] — exactement comme le
ferait JWTAuthentication côté REST, mais pour le protocole WebSocket.
"""

from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError


@database_sync_to_async
def get_user_from_token(token):
    try:
        validated = AccessToken(token)
        User = get_user_model()
        return User.objects.get(id=validated['user_id'])
    except (TokenError, Exception):
        return AnonymousUser()


class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode()
        params = parse_qs(query_string)
        token = params.get('token', [None])[0]

        scope['user'] = await get_user_from_token(token) if token else AnonymousUser()
        return await self.app(scope, receive, send)


def JWTAuthMiddlewareStack(app):
    return JWTAuthMiddleware(app)
