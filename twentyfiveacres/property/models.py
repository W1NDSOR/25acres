# from django.db import models
# from twentyfiveacres.models import Location
# from django.contrib.auth.models import User

# # Remove this (should only be in main models.py)

# # Property Model
# class Property(models.Model):
#     propertId = models.AutoField(primary_key=True)
#     title = models.CharField(max_length=255)
#     description = models.TextField()
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     propertyType = models.CharField(max_length=100)
#     bedrooms = models.PositiveIntegerField()
#     bathrooms = models.PositiveIntegerField()
#     area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     status = models.CharField(
#         max_length=20,
#         choices=[
#             ("for_sale", "For Sale"),
#             ("for_rent", "For Rent"),
#             ("sold", "Sold"),
#             ("rented", "Rented"),
#         ],
#     )
#     availabilityDate = models.DateField()
#     location = models.ForeignKey(Location, on_delete=models.CASCADE)
