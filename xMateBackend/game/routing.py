from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path(
        "ws/game/<str:game_id>/",
        consumers.GameComsumer.as_asgi(),
    ),
]

# pass the game id as the room name 