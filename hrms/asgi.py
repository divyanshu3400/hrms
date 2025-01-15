import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from .routing import websocket_urlpatterns

from decouple import config

DEBUG = config('DEBUG', default=False, cast=bool)

if DEBUG:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms.settings.development')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms.settings.production')


django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        )
    ),
})
