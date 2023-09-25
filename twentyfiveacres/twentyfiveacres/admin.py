from django.contrib import admin
from twentyfiveacres.models import *
from twentyfiveacres.forms import *
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ["rollNumber", "username"]


admin.site.register(User, CustomUserAdmin)
admin.site.register(Property)
admin.site.register(Contract)
