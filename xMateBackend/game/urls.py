from django.urls import path
from . import views

urlpatterns = [
    path('creatematch/',views.createMatchbtwChallengers,name="creatematchbtwchallengers"),
    path('add_player_2/',views.player2joinmatch),
    path('checkif_gamehas_player_2/',views.checkifPlayer_2_hasJoinedGame)
]