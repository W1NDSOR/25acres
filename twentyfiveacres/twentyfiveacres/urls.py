"""
URL configuration for twentyfiveacres project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include, re_path
from django.conf import settings
from . import views

urlpatterns = [
    path("", views.homepage, name="25acres"),
    path("djangoadmin/", views.fake_admin, name="fake_admin"),
    path("admin/", views.fake_admin, name="fake_admin"),
    path("fake/admin/", admin.site.urls),
    path("user/", include("user.urls")),
    path("property/", include("property.urls")),
    path("contracts/", include("contract.urls")),
    path("transaction/", include("transaction.urls")),
    re_path(
        r"^signout/$",
        LogoutView.as_view(),
        {"next_page": settings.LOGOUT_REDIRECT_URL},
        name="signout",
    ),
]
