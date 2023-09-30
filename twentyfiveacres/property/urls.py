from django.urls import path
from .views import *

urlpatterns = [
    path('property/list/', propertyList, name='property_list'),
    path('property/add_bid/<str:property_title>/', add_bid, name='add_bid'),
    path("list/", propertyList, name="propertyList"),
    path("add/", addProperty, name="addProperty"),
]
