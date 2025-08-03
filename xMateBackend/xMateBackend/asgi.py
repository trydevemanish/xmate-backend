"""
ASGI config for xMateBackend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xMateBackend.settings')

# application = get_asgi_application()

import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from game.routing import websocket_urlpatterns
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xMateBackend.settings')


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket" : AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    }
)
