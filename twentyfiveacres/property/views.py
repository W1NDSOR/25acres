from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from twentyfiveacres.models import User, Property, Location
from utils.geocoder import geocode_location
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from user.viewmodel import verifyUserDocument
from django.shortcuts import redirect
from property.viewmodel import generatePropertyHash
from utils.responses import (
    USER_SIGNIN_RESPONSE,
    BIDDING_CLOSED_RESPONSE,
    PROPERTY_DOES_NOT_EXIST_RESPONSE,
)


def propertyList(request):
    if isinstance(request.user, AnonymousUser):
        return redirect("/user/signin")
    properties = Property.objects.filter(listed=True)
    if len(Property.objects.all()) == 0:
        return render(request, "property/property_list.html", {"properties": []})

    if request.method == "GET":
        if selectedType := request.GET.get("type"): 
            properties = properties.filter(status=selectedType)

        selectedBudget = request.GET.get("budget")
        budgetRanges = {
            "Between 1 to 10,00,000": (1, 10_00_000),
            "Between 10,00,001 to 1,00,00,000": (10_00_001, 1_00_00_000),
            "Between 1,00,00,001 to 100,00,00,000": (1_00_00_001, 100_00_00_000),
        }
        if selectedBudget:
            if priceRange := budgetRanges.get(selectedBudget): 
                properties = properties.filter(
                    price__gte=priceRange[0], price__lte=priceRange[1]
                )

        selectedArea = request.GET.get("location_area")
        areaRanges = {
            "Between 1 to 100 acres": (0, 100),
            "Between 101 to 500 acres": (101, 500),
            "Between 501 to 1000 acres": (501, 1000),
        }
        if selectedArea:
            if areaRange := areaRanges.get(selectedArea): 
                properties = properties.filter(
                    area__gte=areaRange[0], area__lte=areaRange[1]
                )

        selectedAvailabilityDate = request.GET.get("availability_date")
        timeRanges = {
            "24hours": "2023-09-29/2023-09-30",
            "7days": "2021-04-01/2021-04-08",
        }
        if selectedAvailabilityDate:
            if (timeRange := timeRanges.get(selectedAvailabilityDate)):
                timeRange = timeRange.split("/")
                properties = properties.filter(
                    availabilityDate__gte=timeRange[0], availabilityDate__lte=timeRange[1]
                )

    context = {
        "properties": properties,
        "error_message": request.GET.get("message"),
    }
    return render(request, "property/property_list.html", context=context)


def addProperty(request):

    if isinstance(request.user, AnonymousUser):
        return USER_SIGNIN_RESPONSE

    if request.method != "POST":
        return render(request, "property/add_form.html")
        
    context = dict()
    propertyFields = request.POST
    title = propertyFields.get("title")
    description = propertyFields.get("description")
    price = propertyFields.get("price")
    bedrooms = propertyFields.get("bedrooms")
    bathrooms = propertyFields.get("bathrooms")
    area = propertyFields.get("area")
    status = propertyFields.get("status")
    rent_duration = int(propertyFields.get('rent_duration', 0))
    rent_duration = rent_duration if status in ["for_rent", "For Rent"] else None
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
    if (
        proofOfIdentity is None
        or verifyUserDocument(user, proofOfIdentity) == False
        or ownershipDocumentHash is None
    ):
        context["error_message"] = "Document hash mismatch. Please check your documents"
        return render(request, "property/add_form.html", context=context) 

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
            if title.isnumeric():
                context["error_message"] = "Title can not be just numbers"
                return render(request, "property/add_form.html", context=context)
            
            if description.isnumeric():
                context["error_message"] = "Description can not be just numbers"
                return render(request, "property/add_form.html", context=context)

            if (
                not price.isnumeric() or
                not area.isnumeric() or
                not bedrooms.isnumeric() or 
                not bathrooms.isnumeric()
            ):
                context["error_message"] = "Numeric fields should not contain text"
                return render(request, "property/add_form.html", context=context)

            price = int(price)
            area = int(area)
            bedrooms = int(bedrooms)
            bathrooms = int(bathrooms)

            if price <= 0 or area <= 0 or bedrooms <= 0 or bathrooms <= 0 :
                context["error_message"] = "Numeric fields cannot be less than or equal to 0"
                return render(request, "property/add_form.html", context=context)

            if proofOfIdentity == ownershipDocumentHash:
                context["error_message"] = "Proof of identity and ownership document cannot be the same"
                return render(request, "property/add_form.html", context=context)
            
            locationCoordinates = geocode_location(location)
            if locationCoordinates is None:
                context["error_message"] = "Not a valid location"
                return render(request, "property/add_form.html", context=context)

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
                rent_duration=rent_duration,
                location=locationObject,
                owner=user,
                originalOwner=user,
                listed=True,
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
            return redirect("/")
        else:
            context["error_message"] = "All fields are not filled"
            return render(request, "property/add_form.html", context=context)
    except Exception as exception:
        print(f"Exception is as follows {exception}")
    return render(request, "property/add_form.html", context=context)


@login_required
@require_POST
def addBid(request, propertyId):
    """
    @desc: adds bid to the property
    @param {Property} propertyId: Id of the property to which bid should should be added
    """

    if isinstance(request.user, AnonymousUser):
        return redirect("/property/list?message=Only signed users are permitted to bid")

    user = User.objects.get(username=request.user.username)

    try:
        property = Property.objects.get(pk=propertyId)
    except ObjectDoesNotExist:
        return PROPERTY_DOES_NOT_EXIST_RESPONSE

    if request.method != "POST":
        return

    bidAmount = request.POST.get("bid_amount")
    if not bidAmount: return redirect("/property/list?message=Bid amount not present")

    if property.owner == user:
        return redirect('/property/list/?message=Owner cannot bid')
    if property.status in ("sold", "Sold", "rented", "Rented"):
        return BIDDING_CLOSED_RESPONSE

    proofOfIdentity = (
        request.FILES["document"].read() if "document" in request.FILES else None
    )
    if proofOfIdentity is None or not verifyUserDocument(user, proofOfIdentity):
        return redirect("/property/list?message=Document hash mismatch. Please check your documents.") 

    if float(bidAmount) > max(property.currentBid, property.price):
        property.currentBid = float(bidAmount)
        property.bidder = user
        property.save()
        return redirect("/property/list?message=Bid placed successfully")
    else:
        return redirect("/property/list?message=Place higher than previous last bid and base price")

@login_required
@require_POST
def report(request, propertyId):
    # check if the user is authenticated
    if isinstance(request.user, AnonymousUser):
        return redirect("../../")

    # check whether propertyId provided is valid or not
    try:
        propertyObj = Property.objects.get(pk=propertyId)
    except ObjectDoesNotExist:
        return JsonResponse(
            {"result": "Treasure not found", "message": "Property does not exist"}
        )

    propertyObj.reported = True
    propertyObj.save()
    return redirect("/property/list?message=Property reported")


def propertyAction(request, propertyId):
    if request.method != "POST":
        return
    if request.POST.get("action") == "place_bid":
        return addBid(request, propertyId)
    elif request.POST.get("action") == "report":
        return report(request, propertyId)
