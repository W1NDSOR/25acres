from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from twentyfiveacres.models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("rollNumber", "username")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("rollNumber", "username")
