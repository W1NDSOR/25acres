# users/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("", views.user_list, name="user_list"),
    path("add/", views.addUser, name="user_add"),
]
