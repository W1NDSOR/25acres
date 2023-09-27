from django.urls import path
from . import views
from django.urls import path
from .views import propertyList, addProperty, add_bid
from django.urls import path
from .views import add_bid, propertyList

urlpatterns = [
    path('property/list/', propertyList, name='property_list'),
    path('property/add_bid/<str:property_title>/', add_bid, name='add_bid'),
    path("list/", views.propertyList, name="propertyList"),
    path("add/", views.addProperty, name="addProperty"),
    # other paths
]
