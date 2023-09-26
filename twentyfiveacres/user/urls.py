from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.signup, name="sign_up"),
    path("signin/", views.signin, name="sign_in"),
    path("profile/", views.profile, name="profile"),
]
