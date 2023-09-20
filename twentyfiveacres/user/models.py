from django.db import models


# User Model
class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    user_type = models.CharField(
        max_length=20,
        choices=[("buyer", "Buyer"), ("seller", "Seller"), ("admin", "Admin")],
    )
    aadhar_number = models.CharField(max_length=20, null=True, blank=True)
    document_hash = models.CharField(max_length=64, null=True, blank=True)
