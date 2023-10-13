from hashlib import sha256
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
from twentyfiveacres.models import User, Property, Location
from utils.geocoder import geocode_location
from utils.hashing import hashDocument
from django.contrib import messages
from utils.exceptions import CustomException
from django.core.exceptions import ObjectDoesNotExist
from user.viewmodel import verifyUserDocument
from property.viewmodel import generatePropertyHash
from utils.responses import (
    USER_SIGNIN_RESPONSE,
    USER_DOCUMENT_HASH_MISMATCH_RESPONSE,
    CANNOT_BID_TO_OWN_PROPERTY_RESPONSE,
    BIDDING_CLOSED_RESPONSE,
)


def propertyList(request):
    """
    @desc: displays the list of properties in the database
    """
    numOfProperties = len(Property.objects.all())
    properties = Property.objects.all()
    if numOfProperties == 0:
        return render(request, "property/property_list.html", {"properties": []})
    

    # Type Button
    selected_type = request.GET.get("type")
    if selected_type:
        properties = properties.filter(status=selected_type)

    # Budget Button
    selected_budget = request.GET.get("budget")
    budget_ranges = {
        "Between 1 to 10,00,000": (1, 10_00_000),
        "Between 10,00,001 to 1,00,00,000": (10_00_001, 1_00_00_000),
        "Between 1,00,00,001 to 100,00,00,000": (1_00_00_001, 100_00_00_000),
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

    # Availability_date Button
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

    bidSuccess = request.GET.get("bid_success") == "True"
    bidError = request.GET.get("bid_error") == "True"
    return render(
        request,
        "property/property_list.html",
        {"properties": properties, "bid_success": bidSuccess, "bid_error": bidError},
    )


def addProperty(request):
    """
    @desc: renders a form for adding new property
    """

    if isinstance(request.user, AnonymousUser):
        return USER_SIGNIN_RESPONSE

    context = dict()

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
        user = User.objects.get(username=request.user.username)

        # Ownership Document Hash
        ownershipDocumentHash = (
            request.FILES["ownership_document"].read()
            if "ownership_document" in request.FILES
            else None
        )

        # Proof of Identity Hash
        proofOfIdentity = (
            request.FILES["document"].read() if "document" in request.FILES else None
        )

        # if either is not correct, do not proceed
        if proofOfIdentity is None or verifyUserDocument(user, proofOfIdentity) == False or ownershipDocumentHash is None:
            return USER_DOCUMENT_HASH_MISMATCH_RESPONSE


        try:
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
                and proofOfIdentity
                and ownershipDocumentHash
            ):
                locationCoordinates = geocode_location(location)
                if locationCoordinates is None:
                    exceptionMessage = "Not a valid location!"
                    messages.info(request, exceptionMessage)
                    raise CustomException(exceptionMessage)
                
                (latitude, longitude) = locationCoordinates
                
                locationObject = Location.objects.create(
                    name=location,
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
                    owner=user,
                    ownershipDocumentHash=ownershipDocumentHash,
                    availabilityDate=availableDate,
                    propertyHashIdentifier=generatePropertyHash(
                        ownershipDocumentHash,
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
        except CustomException as exception:
            pass
        except Exception as exception:
            print(exception)
    return render(request, "property/add_form.html", context=context)


@login_required
@require_POST
def addBid(request, propertyId):
    """
    @desc: adds bid to the property
    @param {Property} propertyId: Id of the property to which bid should should be added
    """

    if isinstance(request.user, AnonymousUser):
        return USER_SIGNIN_RESPONSE
    

    user = User.objects.get(username=request.user.username)

    try:
        property = Property.objects.get(pk=propertyId)
    except ObjectDoesNotExist:
        return JsonResponse(
            {"result": "Treasure not found", "message": "Property does not exist"}
        )

    if request.method != "POST":
        return
    
    bidAmount = request.POST.get("bid_amount")

    if property.owner == user:
        return CANNOT_BID_TO_OWN_PROPERTY_RESPONSE
    if property.status in ("sold", "Sold", "rented", "Rented"):
        return BIDDING_CLOSED_RESPONSE
    
    proofOfIdentity = (
        request.FILES["document"].read() if "document" in request.FILES else None
    )

    if proofOfIdentity is None or verifyUserDocument(user, proofOfIdentity) == False:
        return USER_DOCUMENT_HASH_MISMATCH_RESPONSE

    if bidAmount and float(bidAmount) > property.currentBid:
        property.currentBid = float(bidAmount)
        property.bidder = user
        property.save()
        return HttpResponseRedirect("/property/list?bid_success=True")
    else:
        return HttpResponseRedirect("/property/list?bid_error=True")


@login_required
@require_POST
def report(request, propertyId):
    if request.method != "POST":
        return

    # check if the user is authenticated
    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("../../")

    # check whether propertyId provided is valid or not
    try:
        propertyObj = Property.objects.get(pk=propertyId)
    except ObjectDoesNotExist:
        return JsonResponse(
            {"result": "Treasure not found", "message": "Property does not exist"}
        )

    propertyObj.reported = True
    propertyObj.save()
    return HttpResponseRedirect("/user/profile")
