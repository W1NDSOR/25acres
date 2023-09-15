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
    user_type = models.CharField(max_length=20, choices=[("buyer", "Buyer"), ("seller", "Seller"), ("admin", "Admin")])

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

# Transaction Model
class Transaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, related_name='buyer_transactions', on_delete=models.CASCADE)
    seller = models.ForeignKey(User, related_name='seller_transactions', on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=[("booking", "Booking"), ("down_payment", "Down Payment"), ("full_payment", "Full Payment"), ("rent", "Rent")])
    transaction_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

# Image Model
class Image(models.Model):
    image_id = models.AutoField(primary_key=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    image_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Contract Model (with Blockchain Integration)
class Contract(models.Model):
    contract_id = models.AutoField(primary_key=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    seller = models.ForeignKey(User, related_name='seller_contracts', on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, related_name='buyer_contracts', on_delete=models.CASCADE)
    contract_text = models.TextField()
    contract_hash = models.CharField(max_length=64)  # Hash or identifier for blockchain verification
    contract_address = models.CharField(max_length=255, blank=True, null=True)  # Blockchain contract address (if applicable)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
