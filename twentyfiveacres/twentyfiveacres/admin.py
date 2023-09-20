from django.contrib import admin
from user.models import User
from property.models import Property
from contract.models import Contract


admin.site.register(Property)
admin.site.register(Contract)
admin.site.register(User)
