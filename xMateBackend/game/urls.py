from django.urls import path
from . import views

urlpatterns = [
    path('creatematch/',views.createMatchbtwChallengers,name="creatematchbtwchallengers")
]