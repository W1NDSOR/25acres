from django.urls import path
from . import views

urlpatterns = [
    path('', views.propertyList, name='propertyList'),
]