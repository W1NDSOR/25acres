from django.urls import path
from .views import *

urlpatterns = [
    path("paymentGateway/", paymentGateway, name="paymentGateway"),
    path("cardDetails/", cardDetails, name="cardDetails"),
    path("pay/", pay, name="pay"),
]
