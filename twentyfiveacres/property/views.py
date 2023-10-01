from hashlib import sha256
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.urls import reverse
from twentyfiveacres.models import User, Property, Location
from utils.geocoder import geocode_location
from utils.hashing import hashDocument


def check_document(request):
    document = request.FILES["document"].read()
    documentHash = hashDocument(document)
    if documentHash == User.objects.get(username=request.user.username).documentHash:
        pass
    else:
        return JsonResponse(
            {"result": "Fatal Error", "message": "Document hash does not match"}
        )


def propertyList(request):
    """
    @desc: displays the list of properties in the database
    """
    properties = Property.objects.all()

    # Type Button
    selected_type = request.GET.get("type")
    if selected_type:
        properties = properties.filter(status=selected_type)

    # Budget Button
    selected_budget = request.GET.get("budget")
    budget_ranges = {
        "Between 1 to 1000": (1, 1000),
        "Between 1001 to 5000": (1001, 5000),
        "Between 5001 to 10000": (5001, 10000),
    }
    if selected_budget:
        price_range = budget_ranges.get(selected_budget)
        if price_range:
            properties = properties.filter(
                price__gte=price_range[0], price__lte=price_range[1]
            )

    # Location_Area Button
    selected_location_area = request.GET.get("location_area")
    location_area_ranges = {
        "Between 0 to 100 acres": (0, 100),
        "Between 101 to 500 acres": (101, 500),
        "Between 501 to 1000 acres": (501, 1000),
    }
    if selected_location_area:
        area_range = location_area_ranges.get(selected_location_area)
        if area_range:
            properties = properties.filter(
                area__gte=area_range[0], area__lte=area_range[1]
            )

    # Location_Area Button
    selected_availability_date = request.GET.get("availability_date")
    time_ranges = {
        "24hours": "2023-09-29/2023-09-30",
        "7days": "2021-04-01/2021-04-08",
    }
    if selected_availability_date:
        time_range = time_ranges.get(selected_availability_date)
        if time_range:
            time_range = time_range.split("/")
            properties = properties.filter(
                availabilityDate__gte=time_range[0], availabilityDate__lte=time_range[1]
            )

    # -----------------------------------------------------------------------

    bid_success = request.GET.get("bid_success") == "True"
    bid_error = request.GET.get("bid_error") == "True"
    return render(
        request,
        "property/property_list.html",
        {"properties": properties, "bid_success": bid_success, "bid_error": bid_error},
    )


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
    @return: A unique SHA-256 hash identifier for the property
    """
    concatenated_info = f"{title}{description}{price}{bedrooms}{bathrooms}{area}{status}{location}{availableDate}"
    hash_identifier = sha256(concatenated_info.encode()).hexdigest()

    return hash_identifier


def addProperty(request):
    """
    @desc: renders a form for adding new property
    """

    if isinstance(request.user, AnonymousUser):
        return JsonResponse({"result": "Fatal Error", "message": "Sign in first"})

    if request.method == "POST":
        propertyFields = request.POST

        field_names = [
            "title",
            "description",
            "price",
            "bedrooms",
            "bathrooms",
            "area",
            "status",
            "location",
            "available_date",
        ]
        field_values = {}
        for field_name in field_names:
            field_values[field_name] = propertyFields.get(field_name)
        title = field_values.get("title")
        description = field_values.get("description")
        price = field_values.get("price")
        bedrooms = field_values.get("bedrooms")
        bathrooms = field_values.get("bathrooms")
        area = field_values.get("area")
        status = field_values.get("status")
        location = field_values.get("location")
        availableDate = field_values.get("available_date")

        if "document" in request.FILES:
            check_document(request)

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


@login_required
@require_POST
def addBid(request, propertyId):
    if isinstance(request.user, AnonymousUser):
        return JsonResponse({"result": "Fatal Error", "message": "Sign in first"})
    property = Property.objects.get(propertyId=propertyId)
    user = User.objects.get(username=request.user.username)
    bidAmount = request.POST.get("bid_amount")
    if property.owner == user:
        return JsonResponse(
            {"result": "Identity crisis", "message": "Cannot bid to your own property"}
        )
    if property.status in ("sold", "Sold", "rented", "Rented"):
        return JsonResponse(
            {
                "result": "Time drift exception",
                "message": "Bid already closed",
            }
        )
    if bidAmount and float(bidAmount) > property.currentBid:
        property.currentBid = float(bidAmount)
        property.bidder = user
        property.save()
        return HttpResponseRedirect("/property/list?bid_success=True")
    else:
        return HttpResponseRedirect("/property/list?bid_error=True")
