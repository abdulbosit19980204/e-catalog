import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chat.middleware import JwtAuthMiddleware
import chat.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JwtAuthMiddleware(
        AuthMiddlewareStack(
            URLRouter(
                chat.routing.websocket_urlpatterns
            )
        )
    ),
})
