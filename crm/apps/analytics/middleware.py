from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser


@database_sync_to_async
def _get_user_from_token(token_key):
    """Resolve a DRF auth token to its user. Returns AnonymousUser if invalid."""
    from rest_framework.authtoken.models import Token
    try:
        return Token.objects.select_related('user').get(key=token_key).user
    except Token.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware(BaseMiddleware):
    """Authenticate WebSocket connections via a `?token=` query-string param.

    The browser cannot set Authorization headers on a WebSocket handshake, so
    the frontend passes the DRF token as a query parameter. This populates
    scope['user'] so consumers can enforce authentication.
    """

    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode()
        token_key = parse_qs(query_string).get('token', [None])[0]
        if token_key:
            scope['user'] = await _get_user_from_token(token_key)
        elif 'user' not in scope:
            scope['user'] = AnonymousUser()
        return await super().__call__(scope, receive, send)
