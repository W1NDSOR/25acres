from django.shortcuts import render
from django.http import JsonResponse
from twentyfiveacres.models import Property, Location
from hashlib import sha256
from django.contrib.auth.models import AnonymousUser
from twentyfiveacres.models import User
from utils.geocoder import geocode_location, reverse_geocode
from utils.hashing import hashDocument
from django.http import HttpResponseRedirect


def generatePropertyHashIdentifier(
    title,
    description,
    price,
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
    @param bedrooms: Number of bedrooms in the property
    @param bathrooms: Number of bathrooms in the property
    @param area: Area of the property
    @param status: Status of the property
    @param location: Location of the property
    @param availableDate: Date when the property is available
    @return: A unique SHA-256 hash identifier for the property
    """

    # Concatenate all the property details into one string
    concatenated_info = f"{title}{description}{price}{bedrooms}{bathrooms}{area}{status}{location}{availableDate}"

    # Create a SHA-256 hash of the concatenated string
    hash_identifier = sha256(concatenated_info.encode()).hexdigest()

    return hash_identifier

def propertyList(request):
    """
    @desc: displays the list of properties in the database
    """
    properties = Property.objects.all()
    bid_success = request.GET.get('bid_success') == 'True'
    bid_error = request.GET.get('bid_error') == 'True'
    return render(request, "property/property_list.html", {"properties": properties, "bid_success": bid_success, "bid_error": bid_error})


def addProperty(request):
    """
    @desc: renders a form for adding new user
    """
    if isinstance(request.user, AnonymousUser):
        return JsonResponse({"result": "Fatal Error", "message": "Sign in first"})
    if request.method == "POST":
        propertyFields = request.POST
        title = propertyFields.get("title")
        description = propertyFields.get("description")
        price = propertyFields.get("price")
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
            and bedrooms
            and bathrooms
            and area
            and status
            and location
            and availableDate
        ):
            latitude, longitude = geocode_location(location)
            locationObject = Location.objects.create(
                latitude=latitude,
                longitude=longitude,
            )
            locationObject.save()

            property = Property.objects.create(
                title=title,
                description=description,
                price=price,
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
                    bedrooms,
                    bathrooms,
                    area,
                    status,
                    location,
                    availableDate,
                ),
                currentBid=0,
                bidder=None,
            )
            property.save()
            return HttpResponseRedirect("/")
    return render(request, "property/add_form.html")


from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from twentyfiveacres.models import Property
@login_required
@require_POST
def add_bid(request, property_title):
    property = get_object_or_404(Property, title=property_title)
    user = request.user
    bid_amount = request.POST.get("bid_amount")

    if bid_amount and float(bid_amount) > property.currentBid:
        property.currentBid = float(bid_amount)
        property.bidder = user
        property.save()
        # Redirect to the property list page with a success message
        return HttpResponseRedirect(reverse('property_list') + "?bid_success=True")
    else:
        # Redirect to the property list page with an error message
        return HttpResponseRedirect(reverse('property_list') + "?bid_error=True")
