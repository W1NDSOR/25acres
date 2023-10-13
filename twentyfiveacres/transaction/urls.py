from django.urls import path
from .views import *

urlpatterns = [
    path("paymentGateway/", paymentGateway, name="paymentGateway"),
]
