from django.db import models
from django.contrib.auth.models import AbstractUser


# User Model
class User(AbstractUser):
    """
    User
        @default_django_fields
        id
        password
        last_login
        is_superuser
        username
        last_name
        email
        is_staff
        is_active
        date_joined
        first_name
        user_hash

        @custom_user_fields
        roll_number
        document_hash
        user_hash
    """

    rollNumber = models.IntegerField(unique=True)
    verification_code = models.CharField(max_length=6, null=True, blank=True)
    documentHash = models.CharField(max_length=64, null=True, blank=True)
    userHash = models.CharField(max_length=64, null=False, blank=False)
    REQUIRED_FIELDS = ["rollNumber"]

    def __str__(self):
        return self.username


# Location Model
class Location(models.Model):
    """
    Location
        location_id
        name
        longitude coordinate
        latitude coordinate
    """

    locationId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=False, blank=False)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True)


# Property Model
class Property(models.Model):
    """
    Property
        property_id
        owner
        title
        description
        price
        bedrooms
        bathrooms
        area (location)
        status (available, sold)
        availability_date
        current_bid
        bidder
        TRANSACTION_STATUS_CHOICES
        transaction_status
        ownership_document_hash
        reported
    """

    propertyId = models.AutoField(primary_key=True)
    owner = models.ForeignKey(
        User, related_name="owner", on_delete=models.CASCADE, null=False, blank=False
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=20, decimal_places=2)
    bedrooms = models.PositiveIntegerField()
    bathrooms = models.PositiveIntegerField()
    area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("for_sale", "For Sale"),
            ("for_rent", "For Rent"),
            ("sold", "Sold"),
            ("rented", "Rented"),
        ],
    )
    availabilityDate = models.DateField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    propertyHashIdentifier = models.CharField(max_length=64, null=False, blank=False)
    currentBid = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    bidder = models.ForeignKey(
        User, related_name="current_bidder", on_delete=models.CASCADE, null=True
    )
    TRANSACTION_STATUS_CHOICES = [
        ("not_started", "Not Started"),
        ("initiated_by_seller", "Initiated by Seller"),
        ("initiated_by_buyer", "Initiated by Buyer"),
        ("completed", "Completed"),
    ]

    transactionStatus = models.CharField(
        max_length=20, choices=TRANSACTION_STATUS_CHOICES, default="not_started"
    )
    ownershipDocumentHash = models.CharField(max_length=64, null=False, blank=False)
    reported = models.BooleanField(default=False, null=False, blank=False)


# Transaction Model
class Transaction(models.Model):
    """
    Transactions
        transaction_id
        property_id
        buyer_id
        seller_id
        transaction_date
        amount
        uploaded_document_hash
        transaction_hash_validation
    """

    transactionId = models.AutoField(primary_key=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    buyer = models.ForeignKey(
        User, related_name="buyer_transactions", on_delete=models.CASCADE
    )
    seller = models.ForeignKey(
        User, related_name="seller_transactions", on_delete=models.CASCADE
    )
    transactionType = models.CharField(
        max_length=20,
        choices=[
            ("booking", "Booking"),
            ("down_payment", "Down Payment"),
            ("full_payment", "Full Payment"),
            ("rent", "Rent"),
        ],
    )
    transactionDate = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)


# Image Model
class Image(models.Model):

    """
    Image
        image_id
        property_id
        user_id
        image_url
    """

    imageId = models.AutoField(primary_key=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    imageUrl = models.URLField()
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)


# Contract Model
class Contract(models.Model):
    """
    Contracts
        contract_id
        property_id
        seller_id
        buyer_id
        verified_by_buyer
        verified_by_seller
        verified_by_portal
        contract_hash
        contract_address (blockchain address)
        created_at
    """

    contractId = models.AutoField(primary_key=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    seller = models.ForeignKey(
        User, related_name="seller_contracts", on_delete=models.CASCADE
    )
    buyer = models.ForeignKey(
        User, related_name="buyer_contracts", on_delete=models.CASCADE
    )
    verifiedByBuyer = models.BooleanField(default=False, null=False, blank=False)
    verifiedBySeller = models.BooleanField(default=False, null=False, blank=False)
    verifiedByPortal = models.BooleanField(default=False, null=False, blank=False)
    contractHash = models.CharField(max_length=64)
    contractAddress = models.CharField(max_length=255, blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)


# ----------------------------------------------------------
