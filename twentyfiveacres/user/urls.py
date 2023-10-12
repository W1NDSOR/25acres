from django.urls import path
from . import views


urlpatterns = [
    path("signup/", views.signup, name="sign_up"),
    path("signin/", views.signin, name="sign_in"),
    path("profile/", views.profile, name="profile"),
    path("verify_email/", views.verifyEmail, name="verify_email"),
    path(
        "delete_property/<int:propertyId>/",
        views.deleteProperty,
        name="delete_property",
    ),
    path(
        "contract/<int:propertyId>/",   
        views.handleContract,
        name="handle_contract",
    ),
    path(
        "change_ownership/<int:propertyId>/",
        views.changeOwnership,
        name="change_ownership",
    ),
    path("verify_contract/", views.verifyContract, name="verify_contract"),

]