from django.urls import path
from . import views

urlpatterns = [
    path('',views.fetchleaderBoardResultForAll,name='fetchedleaderboardresult')
]