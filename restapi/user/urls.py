from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView,TokenVerifyView


app_name = "user"  # Optional, but helps with namespacing URLs

urlpatterns = [
    # Define URL patterns for user app views
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path("signin/", views.SigninView.as_view(), name="signin"),
    path("verify_email/", views.VerifyEmailView.as_view(), name="verify_email"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path(
        "delete_property/<int:property_id>/",
        views.DeletePropertyView.as_view(),
        name="delete_property",
    ),
    path(
        "handle_contract/<int:property_id>/",
        views.HandleContractView.as_view(),
        name="handle_contract",
    ),
    path(
        "change_ownership/<int:property_id>/",
        views.ChangeOwnershipView.as_view(),
        name="change_ownership",
    ),
    path(
        "verify_contract/", views.VerifyContractView.as_view(), name="verify_contract"
    ),
]
