from django.urls import path
from .views import *

urlpatterns = [
    path("list/", propertyList, name="propertyList"),
    path("add/", addProperty, name="addProperty"),
    path('addBid/<str:property_title>/', addBid, name='addBid'),
]
