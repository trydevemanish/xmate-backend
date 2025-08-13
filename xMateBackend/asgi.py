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
import sys
import django
from pathlib import Path
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xMateBackend.settings')
django.setup() 

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from game.routing import websocket_urlpatterns
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket" : AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    }
)
