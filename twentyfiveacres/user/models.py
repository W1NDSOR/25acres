# from django.db.models import Model, AutoField, CharField, IntegerField, EmailField

# # Contains the subdivision for Users

# # Remove this (should only be in main models.py)

# # User Model
# class User(Model):
#     userId = AutoField(primary_key=True)
#     userName = CharField(max_length=100, unique=True)
#     email = EmailField(unique=True)
#     password = CharField(max_length=128)
#     firstName = CharField(max_length=100)
#     lastName = CharField(max_length=100)
#     phoneNumber = IntegerField(max_length=10)
#     userType = CharField(max_length=20, choices=[("buyer", "Buyer"), ("seller", "Seller"), ("admin", "Admin")])