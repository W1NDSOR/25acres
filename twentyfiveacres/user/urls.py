from django.urls import path
from . import views

urlpatterns = [
    path("", views.userList, name="user_list"),
    path("add/", views.addUser, name="user_add"),
]
