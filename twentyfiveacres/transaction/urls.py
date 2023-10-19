from django.urls import path
from . import views

urlpatterns = [
    path("paymentGateway/<int:propertyId>/", views.paymentGateway, name="paymentGateway"),
    path("cardDetails/", views.cardDetails, name="cardDetails"),
    path("pay/", views.pay, name="pay"),
]
