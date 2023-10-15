from django.urls import path
from . import views

urlpatterns = [
    path("paymentGateway/", views.PaymentGatewayView.as_view(), name="paymentGateway"),
]
