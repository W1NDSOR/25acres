from django.urls import path
from . import views

urlpatterns = [
    path("", views.userList, name="user_list"),
    path("signup/", views.signup, name="sign_up"),
    path("signin/", views.signin, name="sign_in"),
]
