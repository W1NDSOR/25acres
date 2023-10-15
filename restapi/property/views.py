from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
from restapi.models import User, Property, Location
from utils.geocoder import geocode_location
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
    PROPERTY_DOES_NOT_EXIST_RESPONSE
)

class PropertyListView(APIView):
    def get(self, request):
        # Get query parameters from the request
        selected_type = request.GET.get("type")
        selected_budget = request.GET.get("budget")
        selected_location_area = request.GET.get("location_area")
        selected_availability_date = request.GET.get("availability_date")
        bid_success = request.GET.get("bid_success") == "True"
        bid_error = request.GET.get("bid_error") == "True"

        # Filter properties based on query parameters
        properties = Property.objects.all()

        if selected_type:
            properties = properties.filter(status=selected_type)

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

        time_ranges = {
            "24hours": ["2023-09-29", "2023-09-30"],
            "7days": ["2021-04-01", "2021-04-08"],
        }
        if selected_availability_date:
            date_range = time_ranges.get(selected_availability_date)
            if date_range:
                properties = properties.filter(
                    availabilityDate__range=date_range
                )

        # Convert filtered properties to a list of dictionaries
        properties_data = []
        for prop in properties:
            properties_data.append({
                "property_id": prop.propertyId,
                "title": prop.title,
                # Add more fields as needed
            })

        # Return the list of property dictionaries as JSON response
        response_data = {
            "properties": properties_data,
            "bid_success": bid_success,
            "bid_error": bid_error,
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
class AddPropertyView(APIView):
    def post(self, request):
        """
        @desc: Create a new property
        """

        if isinstance(request.user, AnonymousUser):
            return USER_SIGNIN_RESPONSE  # You need to define this response

        propertyFields = request.data
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
            return Response({"detail": "User document verification failed."}, status=status.HTTP_400_BAD_REQUEST)

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

                return Response({"detail": "Property created successfully."}, status=status.HTTP_201_CREATED)
        except CustomException as exception:
            return Response({"detail": str(exception)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exception:
            return Response({"detail": "An error occurred while creating the property."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """
        @desc: Render a form for adding a new property
        """
        context = dict()

        return Response(context, status=status.HTTP_200_OK)
    

class AddBidView(APIView):
    def post(self, request, propertyId):
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
            return PROPERTY_DOES_NOT_EXIST_RESPONSE

        bidAmount = request.data.get("bid_amount")

        if property.owner == user:
            return Response({"detail": "Cannot bid on your own property."}, status=status.HTTP_400_BAD_REQUEST)
        if property.status in ("sold", "Sold", "rented", "Rented"):
            return Response({"detail": "Bidding is closed for this property."}, status=status.HTTP_400_BAD_REQUEST)

        proofOfIdentity = (
            request.FILES["document"].read() if "document" in request.FILES else None
        )
        if proofOfIdentity is None or not verifyUserDocument(user, proofOfIdentity):
            return Response({"detail": "User document verification failed."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            bidAmount = float(bidAmount)
            if bidAmount > property.currentBid:
                property.currentBid = bidAmount
                property.bidder = user
                property.save()
                return Response({"detail": "Bid added successfully."}, status=status.HTTP_201_CREATED)
            else:
                return Response({"detail": "Bid amount must be higher than the current bid."}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"detail": "Invalid bid amount."}, status=status.HTTP_400_BAD_REQUEST)

class ReportView(APIView):
    def post(self, request, propertyId):
        """
        @desc: Report a property
        """
        # check if the user is authenticated
        if isinstance(request.user, AnonymousUser):
            return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

        # check whether propertyId provided is valid or not
        try:
            propertyObj = Property.objects.get(pk=propertyId)
        except ObjectDoesNotExist:
            return Response({"detail": "Property does not exist."}, status=status.HTTP_404_NOT_FOUND)

        propertyObj.reported = True
        propertyObj.save()
        return Response({"detail": "Property reported successfully."}, status=status.HTTP_200_OK)