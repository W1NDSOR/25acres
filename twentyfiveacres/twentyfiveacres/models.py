from django.db import models

# Contains main entities in the project.

'''
Users
    user_id
    username
    email
    password (hash and salted)
    first_name
    last_name
    phone_number
    user_type (buyer, seller, admin)
    Aadhar Number
    document_hash
    properties_owned
'''

class User(models.Model):
    userId = models.AutoField(primary_key=True)
    userName = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    phoneNumber = models.CharField(max_length=20)
    userType = models.CharField(max_length=20, choices=[("buyer", "Buyer"), ("seller", "Seller"), ("admin", "Admin")])
    aadharNumber = models.CharField(max_length=20, null=True, blank=True)
    documentHash = models.CharField(max_length=64, null=True, blank=True)

'''
Location
    location_id
    street_address
    city
    state
    zip_code
    country
'''

# Location Model
class Location(models.Model):
    locationId = models.AutoField(primary_key=True)
    streetAddress = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipCode = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

'''
Property
    property_id
    title
    description
    price
    property_type
    bedrooms
    bathrooms
    area (location)
    status (available, sold)
    availability_date
'''

# Property Model
class Property(models.Model):
    propertyId = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    propertyType = models.CharField(max_length=100)
    bedrooms = models.PositiveIntegerField()
    bathrooms = models.PositiveIntegerField()
    area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[("for_sale", "For Sale"), ("for_rent", "For Rent"), ("sold", "Sold"), ("rented", "Rented")])
    availabilityDate = models.DateField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

'''
Transactions
    transaction_id
    property_id
    buyer_id
    seller_id
    transaction_date
    amount
    uploaded_document_hash
'''

# Transaction Model
class Transaction(models.Model):
    transactionId = models.AutoField(primary_key=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, related_name='buyer_transactions', on_delete=models.CASCADE)
    seller = models.ForeignKey(User, related_name='seller_transactions', on_delete=models.CASCADE)
    transactionType = models.CharField(max_length=20, choices=[("booking", "Booking"), ("down_payment", "Down Payment"), ("full_payment", "Full Payment"), ("rent", "Rent")])
    transactionDate = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

'''
Image
    image_id
    property_id
    user_id
    image_url
'''

# Image Model
class Image(models.Model):
    imageId = models.AutoField(primary_key=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    imageUrl = models.URLField()
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

'''
Contracts
    contract_id
    property_id
    seller_id
    buyer_id
    contract_text
    contract_hash
    contract_address (blockchain address)
    created_at
'''

# Contract Model 
class Contract(models.Model):
    contractId = models.AutoField(primary_key=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    seller = models.ForeignKey(User, related_name="seller_contracts", on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, related_name="buyer_contracts", on_delete=models.CASCADE)
    contractText = models.TextField()
    contractHash = models.CharField(max_length=64)
    contractAddress = models.CharField(max_length=255, blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)



# ----------------------------------------------------------