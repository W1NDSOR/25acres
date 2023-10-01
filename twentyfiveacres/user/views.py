import ssl
from string import ascii_uppercase, digits
from random import choices
from os import urandom
from hashlib import sha256
from django.urls import reverse
from django.core.mail import send_mail
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AnonymousUser
from twentyfiveacres.models import User, Property, Contract
from utils.hashing import hashDocument
from django.core.exceptions import ObjectDoesNotExist

ssl._create_default_https_context = ssl._create_unverified_context
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


def hash_user(username, roll_number, email):
    """
    Create a hash from the user's details.
    :return: A hexadecimal hash of the user's details.
    """
    salt = urandom(32)

    user_details = f"{username}{roll_number}{email}{salt}"
    user_hash = sha256(user_details.encode()).hexdigest()

    return user_hash


def check_document(request):
    document = request.FILES["document"].read()
    documentHash = hashDocument(document)
    if documentHash == User.objects.get(username=request.user.username).documentHash:
        pass
    else:
        return JsonResponse(
            {"result": "Fatal Error", "message": "Document hash does not match"}
        )


def signup(request):
    """
    @desc: renders a form for signing up new user
    """
    if request.method == "POST":
        userFields = request.POST
        field_names = [
            "user_name",
            "roll_number",
            "email",
            "password",
            "first_name",
            "last_name",
        ]
        field_values = {}
        for field_name in field_names:
            field_values[field_name] = userFields.get(field_name)
        username = field_values.get("user_name")
        rollNumber = field_values.get("roll_number")
        email = field_values.get("email")
        password = field_values.get("password")
        firstName = field_values.get("first_name")
        lastName = field_values.get("last_name")

        if "document" in request.FILES:
            document = request.FILES["document"].read()
            documentHash = hashDocument(document)
        else:
            documentHash = None
        if (
            username
            and email
            and password
            and firstName
            and lastName
            and rollNumber
            and documentHash
        ):
            user_hash = hash_user(username, rollNumber, email)
            verification_code = "".join(choices(ascii_uppercase + digits, k=6))
            user = User.objects.create(
                username=username,
                email=email,
                rollNumber=rollNumber,
                password=make_password(password),
                first_name=firstName,
                last_name=lastName,
                documentHash=documentHash,
                userHash=user_hash,
                verification_code=verification_code,
            )
            user.save()
            send_mail(
                "Welcome to 25acres",
                f"Your verification code is {verification_code}",
                "settings.EMAIL_HOST_USER",
                [email],
                fail_silently=False,
            )

            return HttpResponseRedirect(reverse("verify_email"))

    return render(request, "user/signup_form.html")


def verify_email(request):
    if request.method == "POST":
        code = request.POST.get("code")
        rollNumber = request.POST.get("roll_number")
        try:
            user = User.objects.get(rollNumber=rollNumber, verification_code=code)
            user.verification_code = None
            user.save()
            return HttpResponseRedirect("../signin")
        except User.DoesNotExist:
            return render(
                request,
                "user/verify_email.html",
                {"error": "Invalid code or roll number"},
            )
    return render(request, "user/verify_email.html")


def signin(request):
    """
    @desc: renders a form for signing up new user
    """
    if request.method == "POST":
        userFields = request.POST
        rollNumber = userFields.get("roll_number")
        password = userFields.get("password")
        if rollNumber and password:
            try:
                user = User.objects.get(rollNumber=rollNumber)
                salt = user.password.split("$")[2]
                if user.password == make_password(password, salt=salt):
                    login(request, user)
                    return HttpResponseRedirect("../../")
            except:
                pass
    return render(request, "user/signin_form.html")


def profile(request):
    """
    @desc: renders a page where signed in user can view/update their profile
    """

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("../../")
    user = User.objects.get(username=request.user.username)

    properties = Property.objects.filter(owner=user)
    contracts = []
    for property in properties:
        try:
            contracts.append(Contract.objects.get(property=property))
        except ObjectDoesNotExist:
            contracts.append(None)

    propertyBidings = Property.objects.filter(bidder=user)
    propertyBidingsContracts = []
    for property in propertyBidings:
        try:
            propertyBidingsContracts.append(Contract.objects.get(property=property))
        except ObjectDoesNotExist:
            propertyBidingsContracts.append(None)

    context = {
        "username": user.username,
        "roll_number": user.rollNumber,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "properties": properties,
        "contracts": contracts,
        "propertyBindings": propertyBidings,
        "propertyBidingsContracts": propertyBidingsContracts,
    }

    if request.method == "POST":
        if "action" in request.POST:
            button_value = request.POST["action"]

        if button_value == "profileDetailButton":
            userFields = request.POST
            firstName = userFields.get("first_name")
            lastName = userFields.get("last_name")
            if firstName and lastName:
                user.first_name = firstName
                user.last_name = lastName
                user.save()
                return HttpResponseRedirect("/")

        elif button_value == "sellProperty":
            if "document" in request.FILES:
                check_document(request)
            else:
                print("Upload document")
                return HttpResponseRedirect("/")

            property.status = "Sold"
            return render("transaction/transaction1.html")

    return render(request, "user/profile.html", context=context)


def deleteProperty(request, propertyId):
    """
    @desc: deletes property with propertyId if user is the owner of the property
    @params {int} propertyId: Id of the property to be deleted
    """
    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("../../")

    user = User.objects.get(username=request.user.username)
    try:
        property = Property.objects.get(propertyId=propertyId)
        if property.owner == user:
            property.delete()
            return HttpResponseRedirect("/")
        else:
            return JsonResponse(
                {
                    "result": "Identity Crisis",
                    "message": "You are not the owner of this property",
                }
            )
    except ObjectDoesNotExist:
        return JsonResponse(
            {"result": "Treasure not found", "message": "Property does not exist"}
        )


def handleContract(request, propertyId):
    """
    @desc: handles everything related to a contract
    """

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("../../")
    user = User.objects.get(username=request.user.username)

    try:
        property = Property.objects.get(propertyId=propertyId)
        if property.owner != user and property.bidder != user:
            return JsonResponse(
                {
                    "result": "Identity Crisis",
                    "message": "You are not the bidder nor the owner of this property",
                }
            )
    except ObjectDoesNotExist:
        return JsonResponse(
            {"result": "Treasure not found", "message": "Property does not exist"}
        )

    try:
        contract = Contract.objects.get(property=propertyId)
    except ObjectDoesNotExist:
        contract = None

    if contract is None and property.owner == user:
        contract = Contract.objects.create(
            property=property,
            seller=user,
            buyer=property.bidder,
            verifiedByBuyer=False,
            verifiedBySeller=True,
            verifiedByPortal=False,
            contractHash="",
            contractAddress=None,
        )
        contract.save()
        return HttpResponseRedirect("/user/profile")

    if (
        contract is not None
        and not contract.verifiedByBuyer
        and not contract.verifiedByPortal
        and contract.verifiedBySeller
        and property.bidder == user
    ):
        # contract.verifiedByBuyer = True
        # update contract
        # verify contract by buyer
        # verify contract by portal
        # update property
        # proceed to payment gateway
        # redirect to profiles
        # notify both parties
        return JsonResponse(
            {"result": "Yahoo", "message": "Contract verified from your end"}
        )

    return JsonResponse(
        {"result": "Trespassing", "message": "Wandering into unbeknownst valleys"}
    )
