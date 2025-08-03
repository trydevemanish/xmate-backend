from django.urls import path
from . import views

urlpatterns = [
    path('register/',views.registerUser,name="registeruser"),
    path('login/',views.loginUser,name="loginuser"),
    path('logout/',views.logoutUser,name="logout"),
    path('user/info/',views.fetchLoginUserdetail,name="fetchuserdetail"),
    path('check_rank/',views.fetchAllUserForPlayerRank),
]