from django.shortcuts import render
from django.http import JsonResponse
from twentyfiveacres.models import Property, Location
from hashlib import sha256
from django.contrib.auth.models import AnonymousUser
from twentyfiveacres.models import User
from utils.geocoder import geocode_location, reverse_geocode
from utils.hashing import hashDocument


def generatePropertyHashIdentifier(
    title,
    description,
    price,
    propertyType,
    bedrooms,
    bathrooms,
    area,
    status,
    location,
    availableDate,
):
    """
    @desc: generates a unique hash identifier for a property based on its details
    @param title: Title of the property
    @param description: Description of the property
    @param price: Price of the property
    @param propertyType: Type of the property
    @param bedrooms: Number of bedrooms in the property
    @param bathrooms: Number of bathrooms in the property
    @param area: Area of the property
    @param status: Status of the property
    @param location: Location of the property
    @param availableDate: Date when the property is available
    @return: A unique SHA-256 hash identifier for the property
    """

    # Concatenate all the property details into one string
    concatenated_info = f"{title}{description}{price}{propertyType}{bedrooms}{bathrooms}{area}{status}{location}{availableDate}"

    # Create a SHA-256 hash of the concatenated string
    hash_identifier = sha256(concatenated_info.encode()).hexdigest()

    return hash_identifier


def propertyList(request):
    """
    @desc: displays the list of properties in the database
    """
    properties = Property.objects.all()
    return render(request, "property/property_list.html", {"properties": properties})


def addProperty(request):
    """
    @desc: renders a form for adding new user
    """
    if isinstance(request.user, AnonymousUser):
        return JsonResponse(
            {"result": "Fatal Error", "message": "Sign in as Seller first"}
        )
    if request.method == "POST":
        propertyFields = request.POST
        title = propertyFields.get("title")
        description = propertyFields.get("description")
        price = propertyFields.get("price")
        propertyType = propertyFields.get("property_type")
        bedrooms = propertyFields.get("bedrooms")
        bathrooms = propertyFields.get("bathrooms")
        area = propertyFields.get("area")
        status = propertyFields.get("status")
        location = propertyFields.get("location")
        availableDate = propertyFields.get("available_date")
        if "document" in request.FILES:
            document = request.FILES["document"].read()
            documentHash = hashDocument(document)
            if documentHash == User.objects.get(username=request.user.username).documentHash:
                pass
            else:
                return JsonResponse(
                    {"result": "Fatal Error", "message": "Document hash does not match"}
                )
        # just a precaution, as all the fields are required
        if (
            title
            and description
            and price
            and propertyType
            and bedrooms
            and bathrooms
            and area
            and status
            and location 
            and availableDate
        ):
            latitude, longitude = geocode_location(location)
            locationObject = Location.objects.create(
                latitude = latitude,
                longitude = longitude,
            )
            locationObject.save()
            
            Property.objects.create(
                title=title,
                description=description,
                price=price,
                propertyType=propertyType,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                area=area,
                status=status,
                location=locationObject,
                owner=User.objects.get(username=request.user.username),
                availabilityDate=availableDate,
                propertyHashIdentifier=generatePropertyHashIdentifier(
                    title,
                    description,
                    price,
                    propertyType,
                    bedrooms,
                    bathrooms,
                    area,
                    status,
                    location,
                    availableDate,
                ),
            )
    return render(request, "property/add_form.html")
