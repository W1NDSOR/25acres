from django.urls import path
from . import views

urlpatterns = [
    path('', views.play_video, name='play_video'),
]
