from django.urls import re_path
from . import consumers

# websocket_urlpatterns = [
#     path(
#         "ws/game/<str:game_id>/",
#         consumers.GameComsumer.as_asgi(),
#     ),
# ]


websocket_urlpatterns = [
    re_path(
        r"ws/game/(?P<game_id>[0-9a-f-]+)/$",
        consumers.GameComsumer.as_asgi(),
    ),
]

# pass the game id as the room name 