from django.contrib import admin
from .models import Property, Transaction, User  # Import your models

admin.site.register(Property)
admin.site.register(Transaction)
admin.site.register(User)
