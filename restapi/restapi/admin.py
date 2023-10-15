from django.contrib import admin
from .models import Property
from .models import User
from .models import Contract
from .models import Location


admin.site.register(Property)
admin.site.register(User)
admin.site.register(Contract)
admin.site.register(Location)
