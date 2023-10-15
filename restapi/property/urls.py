from django.urls import path
from . import views

from django.urls import path
from . import views

urlpatterns = [
    
    path("list/", views.PropertyListView.as_view(), name="propertyList"),
    path("add/", views.AddPropertyView.as_view(), name="addProperty"),
    path('add_bid/<int:propertyId>/', views.AddBidView.as_view(), name='add_bid'),
    path('report/<int:propertyId>/', views.ReportView.as_view(), name='report_property'),
]
