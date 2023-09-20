from django.urls import path
from .views import *

urlpatterns = [
    path("", listContracts, name="contracts_list"),
]
