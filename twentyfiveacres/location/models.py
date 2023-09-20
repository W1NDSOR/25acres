from django.db.models import Model, AutoField, CharField


class Location(Model):
    location_id = AutoField(primary_key=True)
    street_address = CharField(max_length=255)
    city = CharField(max_length=100)
    state = CharField(max_length=100)
    zip_code = CharField(max_length=20)
    country = CharField(max_length=100)
