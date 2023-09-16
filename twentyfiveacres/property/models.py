from django.db import models

# Create your models here.

# Location Model
class Location(models.Model):
    location_id = models.AutoField(primary_key=True)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

# Property Model
class Property(models.Model):
    property_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    property_type = models.CharField(max_length=100)
    bedrooms = models.PositiveIntegerField()
    bathrooms = models.PositiveIntegerField()
    area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[("for_sale", "For Sale"), ("for_rent", "For Rent"), ("sold", "Sold"), ("rented", "Rented")])
    availability_date = models.DateField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE)