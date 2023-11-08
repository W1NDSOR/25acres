from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
from twentyfiveacres.models import User, Property, Location
from utils.geocoder import geocode_location
from django.contrib import messages
from utils.exceptions import CustomException
from django.core.exceptions import ObjectDoesNotExist
from user.viewmodel import verifyUserDocument
from django.shortcuts import redirect
from property.viewmodel import generatePropertyHash
from utils.responses import (
    USER_SIGNIN_RESPONSE,
    USER_DOCUMENT_HASH_MISMATCH_RESPONSE,
    CANNOT_BID_TO_OWN_PROPERTY_RESPONSE,
    BIDDING_CLOSED_RESPONSE,
    PROPERTY_DOES_NOT_EXIST_RESPONSE,
)


from web3 import Web3
from web3.middleware import geth_poa_middleware

node_url = 'https://rpc.sepolia.org'
w3 = Web3(Web3.HTTPProvider(node_url))
if w3.is_connected():
    print("Connected to the Ethereum node: ", node_url)
else:
    print("Could not connect to the Ethereum node: ", node_url)
    exit(1)



w3.middleware_onion.inject(geth_poa_middleware, layer=0)

ethereum_account = '0x7c816034A35AC2BFd92f04F73C428C9805584f41'
private_key = "" # private key
lower_case_address = '0xba204c7da7b417f0553fef66f95c67aab0a1fc6f'
contract_address = Web3.to_checksum_address(lower_case_address)


nonce = w3.eth.get_transaction_count(ethereum_account)

contract_abi = [
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "title",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "description",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "price",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "bedrooms",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "bathrooms",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "area",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "status",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "location",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "availableDate",
				"type": "string"
			}
		],
		"name": "listProperty",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "properties",
		"outputs": [
			{
				"internalType": "string",
				"name": "title",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "description",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "price",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "bedrooms",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "bathrooms",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "area",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "status",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "location",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "availableDate",
				"type": "string"
			},
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			},
			{
				"internalType": "bool",
				"name": "listed",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]


contract = w3.eth.contract(address=contract_address, abi=contract_abi)

print("Contract:", contract)


def propertyList(request):
    """
    @desc: displays the list of properties in the database
    """
    numOfProperties = len(Property.objects.all())
    properties = Property.objects.filter(listed=True)
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
        print("title type:", type(title))
        description = propertyFields.get("description")
        print("description type:", type(description))
        price = propertyFields.get("price")
        print("price type:", type(price))
        bedrooms = propertyFields.get("bedrooms")
        print("bedrooms type:", type(bedrooms))
        bathrooms = propertyFields.get("bathrooms")
        print("bathrooms type:", type(bathrooms))
        area = propertyFields.get("area")
        print("area type:", type(area))
        status = propertyFields.get("status")
        print("status type:", type(status))
        rent_duration = int(propertyFields.get('rent_duration', 0))
        rent_duration = rent_duration if status in ["for_rent", "For Rent"] else None
        location = propertyFields.get("location")
        print("location type:", type(location))
        availableDate = propertyFields.get("available_date")
        print("availableDate type:", type(availableDate))
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
            messages.error(request, "Document hash mismatch. Please check your documents.")
            return redirect(propertyList) 

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
                print(rent_duration),
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


                # # Blockchain (uncomment it)
                # chain_id = w3.eth.chain_id
                # call_function = contract.functions.listProperty(title, description, price, bedrooms, bathrooms, area, status, location, availableDate).build_transaction({
                # 'chainId': chain_id,
                # 'nonce': nonce,
                # 'gas': 1000000,
                # })

                # signed_tx = w3.eth.account.sign_transaction(call_function, private_key=private_key)
                # send_tx = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

                # tx_receipt = w3.eth.wait_for_transaction_receipt(send_tx)
                # print("receipt:", tx_receipt)

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
        return PROPERTY_DOES_NOT_EXIST_RESPONSE

    if request.method != "POST":
        return

    bidAmount = request.POST.get("bid_amount")

    if property.owner == user:
        return redirect('/property/list/?bid_error=True')
    if property.status in ("sold", "Sold", "rented", "Rented"):
        return BIDDING_CLOSED_RESPONSE

    proofOfIdentity = (
        request.FILES["document"].read() if "document" in request.FILES else None
    )
    if proofOfIdentity is None or not verifyUserDocument(user, proofOfIdentity):
            messages.error(request, "Document hash mismatch. Please check your documents.")
            return redirect(propertyList) 

    if bidAmount and float(bidAmount) > max(property.currentBid, property.price):
        property.currentBid = float(bidAmount)
        property.bidder = user
        messages.success(request, "Bid placed successfully")
        property.save()
        return HttpResponseRedirect("/property/list?bid_success=True")
    else:
        return HttpResponseRedirect("/property/list?bid_error=True")


@login_required
@require_POST
def report(request, propertyId):
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
    return HttpResponseRedirect("/property/list")


def propertyAction(request, propertyId):
    if request.method != "POST":
        return
    if request.POST.get("action") == "place_bid":
        return addBid(request, propertyId)
    elif request.POST.get("action") == "report":
        return report(request, propertyId)
