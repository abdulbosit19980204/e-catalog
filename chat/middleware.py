from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt import decode as jwt_decode
from django.conf import settings
from urllib.parse import parse_qs

User = get_user_model()

@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class JwtAuthMiddleware:
    """
    Custom middleware that takes a token from the query string and authenticates the user.
    Usage: ws://host:port/ws/chat/1/?token=ACCESS_TOKEN
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Close old database connections to prevent usage of timed out connections
        # from django.db import close_old_connections
        # close_old_connections()

        # Get the token from query string
        query_string = scope.get("query_string", b"").decode("utf-8")
        query_params = parse_qs(query_string)
        token = query_params.get("token", [None])[0]

        if not token:
            # Fallback to headers if not in query string (though harder for browser WS)
            headers = dict(scope.get("headers", []))
            if b"authorization" in headers:
                try:
                    auth_header = headers[b"authorization"].decode("utf-8")
                    if auth_header.startswith("Bearer "):
                        token = auth_header.split(" ")[1]
                except Exception:
                    token = None

        if token:
            try:
                # This will automatically validate the token and raise an error if invalid
                UntypedToken(token)
                
                # Decode the token to get the user ID
                decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                # SimpleJWT uses 'user_id' by default
                user_id = decoded_data.get("user_id")
                
                if user_id:
                    scope["user"] = await get_user(user_id)
                else:
                    scope["user"] = AnonymousUser()
            except (InvalidToken, TokenError, Exception) as e:
                print(f"WebSocket Auth Error: {e}")
                scope["user"] = AnonymousUser()
        else:
            # If no token, check if they are already authenticated via session (for browser users)
            if "user" not in scope or scope["user"].is_anonymous:
                scope["user"] = AnonymousUser()

        return await self.inner(scope, receive, send)

def JwtAuthMiddlewareStack(inner):
    return JwtAuthMiddleware(inner)
