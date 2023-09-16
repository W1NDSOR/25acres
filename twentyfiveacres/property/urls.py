# property/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.property_list, name='property_list'),
]