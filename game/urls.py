from django.urls import path
from . import views

urlpatterns = [
    path('creatematch/',views.createMatchbtwChallengers,name="creatematchbtwchallengers"),
    path('add_player_2/',views.player2joinmatch),
    path('checkif_gamehas_player_2/',views.checkifPlayer_2_hasJoinedGame),
    path('pending_game/',views.finding_user_pending_or_inprogess_games),
    path('recent_game/',views.finding_user_recent_two_games),
    path('game_instance/',views.fetchGameData),
    path('user_involved_in_games/',views.find_game_in_which_userisinvolved_can_be_pendingorcompleted),
    path('delete_game/',views.delete_a_game),
    path('updatestats_aftercheckmate/',views.UpdateGameStatsAfterWinning),
]