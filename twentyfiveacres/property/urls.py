from django.urls import path
from . import views

urlpatterns = [
    path("list/", views.propertyList, name="propertyList"),
    path("add/", views.addProperty, name="addProperty"),
]
