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
        wallet
    """

    rollNumber = models.IntegerField(unique=True)
    verificationCode = models.CharField(max_length=6, null=True, blank=True)
    documentHash = models.CharField(max_length=64, null=True, blank=True)
    userHash = models.CharField(max_length=64, null=False, blank=False)
    wallet = models.IntegerField(default=1000000000, null=False, blank=False)
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
    ownershipDocumentHash = models.CharField(max_length=64, null=False, blank=False)
    reported = models.BooleanField(default=False, null=False, blank=False)


# Seller Contract Model
class SellerContract(models.Model):
    """
    Contracts
        contract_hash_identifier [PK]
        property
        seller
        created_at
        updated_at
        contract_address (blockchain address)
    """

    contractHashIdentifier = models.CharField(
        max_length=64, primary_key=True, null=False, blank=False
    )

    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    seller = models.ForeignKey(
        User, related_name="seller_contract", on_delete=models.CASCADE
    )

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    contractAddress = models.CharField(max_length=255, blank=True, null=True)


# Buyer Contract Model
class BuyerContract(models.Model):
    """
    Contracts
        contract_hash_identifier [PK]
        property
        buyer
        created_at
        updated_at
        contract_address (blockchain address)
    """

    contractHashIdentifier = models.CharField(
        max_length=64, primary_key=True, null=False, blank=False
    )
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    buyer = models.ForeignKey(
        User, related_name="buyer_contract", on_delete=models.CASCADE
    )
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    contractAddress = models.CharField(max_length=255, blank=True, null=True)


# Contract Model
class Contract(models.Model):
    """
    Contract
        property
        seller_contract
        buyer_contract
    """

    property = models.OneToOneField(
        Property, on_delete=models.CASCADE, verbose_name="related_proprety"
    )
    sellerContract = models.ForeignKey(
        SellerContract,
        on_delete=models.CASCADE,
        related_name="related_seller_contract",
        default=None,
    )
    buyerContract = models.ForeignKey(
        BuyerContract,
        on_delete=models.CASCADE,
        related_name="related_buyer_contract",
        default=None,
        null=True,
        blank=True,
    )


class SHA(models.Model):
    """
    SHA
        sha
    """

    sha = models.CharField(max_length=64, primary_key=True, null=False, blank=False)


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


# ----------------------------------------------------------
