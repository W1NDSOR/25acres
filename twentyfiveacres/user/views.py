import ssl
from django.core.mail import send_mail
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AnonymousUser
from utils.hashing import hashDocument, generateGcmOtp
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from user.viewmodel import generateUserHash, verifyUserDocument
from property.viewmodel import generatePropertyHash
from os import urandom
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.backends import default_backend
from base64 import b64decode
from contract.viewmodel import (
    generateUserPropertyContractHash,
    getAbstractContractArray,
)
from utils.responses import (
    USER_SIGNIN_RESPONSE,
    USER_DOCUMENT_HASH_MISMATCH_RESPONSE,
    USER_EMAIL_ROLLNUMBER_MISMATCH_RESPONSE,
    USER_INVALID_EMAIL_FORMAT_RESPONSE,
    USER_INVALID_CODE_OR_ROLLNUMBER_RESPONSE,
    USER_INVALID_ROLLNUMBER_RESPONSE,
    USER_NOT_OWNER_RESPONSE,
    PROPERTY_DOES_NOT_EXIST_RESPONSE,
    USER_NOT_BIDDER_NOR_OWNER_RESPONSE,
    TRESPASSING_RESPONSE,
    PROPERTY_OWNERSHIP_DOCUMENT_MISSING_RESPONSE,
)
from twentyfiveacres.models import (
    User,
    Property,
    Contract,
    SellerContract,
    BuyerContract,
)
from utils.crypto import (
    verifyWithPortalPublicKey,
    encryptWithUserSha,
    decryptWithUserSha,
    signWithPortalPrivateKey,
    PORTAL_PRIVATE_KEY,
    PORTAL_PUBLIC_ENCODED_KEY,
)

secretKey = urandom(16)

ssl._create_default_https_context = ssl._create_unverified_context
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


def signup(request):
    """
    @desc: renders a form for signing up new user
    """

    if request.method == "POST":
        userFields = request.POST
        username = userFields.get("user_name")
        rollNumber = userFields.get("roll_number")
        email = userFields.get("email")
        password = userFields.get("password")
        firstName = userFields.get("first_name")
        lastName = userFields.get("last_name")

        # Roll No and Email Validation
        try:
            extractedRollSuffix = email.split("@")[0][-5:]
            if extractedRollSuffix != rollNumber[-5:]:
                # return USER_EMAIL_ROLLNUMBER_MISMATCH_RESPONSE
                pass # (For testing)
        except:
            return USER_INVALID_EMAIL_FORMAT_RESPONSE

        documentHash = (
            hashDocument(request.FILES["document"].read())
            if "document" in request.FILES
            else None
        )

        if (
            username
            and email
            and password
            and firstName
            and lastName
            and rollNumber
            and documentHash
        ):
            verificationCode = generateGcmOtp(secretKey, rollNumber.encode())
            user = User.objects.create(
                username=username,
                email=email,
                rollNumber=rollNumber,
                password=make_password(password),
                first_name=firstName,
                last_name=lastName,
                documentHash=documentHash,
                userHash=generateUserHash(username, rollNumber, email),
                verificationCode=verificationCode,
            )
            user.save()
            send_mail(
                "Welcome to 25acres",
                f"Your verification code is {verificationCode}",
                "settings.EMAIL_HOST_USER",
                [email],
                fail_silently=False,
            )

            return HttpResponseRedirect("/user/verify_email")

    return render(request, "user/signup_form.html")


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
                    return HttpResponseRedirect("/")
            except User.DoesNotExist:
                return USER_INVALID_ROLLNUMBER_RESPONSE
    return render(request, "user/signin_form.html")


# Profile and Property

def profile(request):
    """
    @desc: renders a page where signed in user can view/update their profile
    """

    if isinstance(request.user, AnonymousUser):
        return USER_SIGNIN_RESPONSE

    user = User.objects.get(username=request.user.username)
    numProperties = Property.objects.filter(owner=user).count()

    properties = Property.objects.filter(
        owner=user, status__in=["for_sell", "For Sell", "for_rent", "For Rent"]
    )

    contracts = getAbstractContractArray(properties)
    propertyBidings = Property.objects.filter(
        bidder=user, status__in=["for_sell", "For Sell", "for_rent", "For Rent"]
    )

    propertyBidingsContracts = getAbstractContractArray(propertyBidings)
    pastProperties = Property.objects.filter(
        Q(owner=user) | Q(bidder=user), status__in=["Sold", "Rented"]
    )

    if numProperties == 0:
        return render(request, "user/profile.html", context={"username": user.username, "roll_number": user.rollNumber, "email": user.email, "first_name": user.first_name, "last_name": user.last_name, "properties": properties, "contracts": contracts, "propertyBindings": propertyBidings, "propertyBidingsContracts": propertyBidingsContracts, "pastProperties": pastProperties })

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
        "pastProperties": pastProperties,
    }

    if request.method == "POST" and request.POST.get("action") == "profileDetailButton":
        userFields = request.POST
        firstName = userFields.get("first_name")
        lastName = userFields.get("last_name")
        if firstName and lastName:
            user.first_name = firstName
            user.last_name = lastName
            user.save()
            return HttpResponseRedirect("/")
    
    return render(request, "user/profile.html", context=context)


def deleteProperty(request, propertyId):
    """
    @desc: deletes property with propertyId if user is the owner of the property
    @params {int} propertyId: Id of the property to be deleted
    """

    if isinstance(request.user, AnonymousUser):
        return USER_SIGNIN_RESPONSE

    user = User.objects.get(username=request.user.username)
    try:
        property = Property.objects.get(propertyId=propertyId)
        if property.owner == user:
            property.delete()
            return HttpResponseRedirect("/")
        else:
            return USER_NOT_OWNER_RESPONSE
    except ObjectDoesNotExist:
        return PROPERTY_DOES_NOT_EXIST_RESPONSE


def handleContract(request, propertyId):
    """
    @desc: handles everything related to a contract
    """

    if isinstance(request.user, AnonymousUser):
        return USER_SIGNIN_RESPONSE
    user = User.objects.get(username=request.user.username)

    try:
        property = Property.objects.get(propertyId=propertyId)
    except ObjectDoesNotExist:
        return PROPERTY_DOES_NOT_EXIST_RESPONSE

    if property.owner != user and property.bidder != user:
        return USER_NOT_BIDDER_NOR_OWNER_RESPONSE

    try:
        contract = Contract.objects.get(property=propertyId)
    except ObjectDoesNotExist:
        contract = None

    # hardcoded the private key for the portal
    if contract is None and property.owner == user:
        sellerContract = SellerContract.objects.create(
            property=property,
            seller=user,
            contractHash=generateUserPropertyContractHash(user, property),
            contractAddress=None,
        )
        sellerContract.save()
        contract = Contract.objects.create(
            property=property,
            seller=sellerContract,
        )
        contract.save()
        # contract hash
        contractHash = sellerContract.contractHashIdentifier
        signature = signWithPortalPrivateKey(PORTAL_PRIVATE_KEY, contractHash)
        encryptedSignature = encryptWithUserSha(user.userHash, signature)
        # TODO: now need to mail these both things `contractHash` and `encryptedSignature` to the user

        return HttpResponseRedirect("/user/profile")

    if (
        contract is not None
        and contract.sellerContract is not None
        and contract.buyerContract is None
        and property.bidder == user
    ):
        buyerContract = BuyerContract.objects.create(
            property=property,
            buyer=user,
            contractHash=generateUserPropertyContractHash(user, property),
            contractAddress=None,
        )
        buyerContract.save()
        contractHash = buyerContract.contractHashIdentifier
        signature = signWithPortalPrivateKey(PORTAL_PRIVATE_KEY, contractHash)
        encryptedSignature = encryptWithUserSha(user.userHash, signature)
        # TODO: now need to mail these both things `contractHash` and `encryptedSignature` to the user

        contract.buyerContract = buyerContract
        contract.save()
        if property.status in ("for_sell", "For Sell"):
            property.status = "Sold"
        elif property.status in ("for_rent", "For Rent"):
            property.status = "Rented"
        property.save()
        return HttpResponseRedirect("/user/profile")

    return TRESPASSING_RESPONSE


def changeOwnership(request, propertyId):
    if request.method != "POST":
        TRESPASSING_RESPONSE

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("../../")

    user = User.objects.get(username=request.user.username)
    try:
        propertyObj = Property.objects.get(pk=propertyId)
    except ObjectDoesNotExist:
        return PROPERTY_DOES_NOT_EXIST_RESPONSE

    # Won't occur
    if propertyObj.owner != user:
        return USER_NOT_OWNER_RESPONSE

# --------------------------------------------------------------------------------------------

    proofOfIdentity = request.FILES.get(f"proof_identity_{propertyId}")
    if not proofOfIdentity or not verifyUserDocument(user, proofOfIdentity):
        return USER_DOCUMENT_HASH_MISMATCH_RESPONSE

    ownershipDocumentHash = (
        hashDocument(request.FILES[f"ownership_document_{propertyId}"].read())
        if f"ownership_document_{propertyId}" in request.FILES
        else None
    )

    if ownershipDocumentHash is None:
        return PROPERTY_OWNERSHIP_DOCUMENT_MISSING_RESPONSE

    # Update ownership document if it is not None (it cannot be None, cause field required while adding property)
    ownershipDocumentHash = ownershipDocumentHash
    propertyObj.ownershipDocumentHash = ownershipDocumentHash
    propertyObj.propertyHashIdentifier = generatePropertyHash(
        ownershipDocumentHash,
        propertyObj.title,
        propertyObj.description,
        propertyObj.price,
        propertyObj.bedrooms,
        propertyObj.bathrooms,
        propertyObj.area,
        propertyObj.status,
        propertyObj.location.name,
        propertyObj.availabilityDate,
    )
    propertyObj.save()
    return HttpResponseRedirect("/user/profile")


def verifyContract(request):
    try:
        if request.method == "POST":
            verificationText = request.POST.get("verification_string")
            verificationTextBytes = b64decode(verificationText)
            contractShaDigest = b64decode(request.POST.get("contract_sha"))

            # TODO: replace this logic with environment variable
            portalPublicKeyBytes = b64decode(PORTAL_PUBLIC_ENCODED_KEY)
            portalPublicKey = load_pem_public_key(
                portalPublicKeyBytes, backend=default_backend()
            )

            username = request.POST.get("user_identifier")
            user = User.objects.get(username=username)
            userSha = b64decode(user.userHash)

            decryptedSignature = decryptWithUserSha(userSha, verificationTextBytes)
            verifiedContractSha = verifyWithPortalPublicKey(
                portalPublicKey, contractShaDigest, decryptedSignature
            )

            if verifiedContractSha == contractShaDigest:
                verification_result = "sanctioned"
            else:
                verification_result = "not_sanctioned"

            print(verification_result)
            context = {"verification_result": verification_result}

            return HttpResponseRedirect("/user/profile")

        return HttpResponseRedirect("/user/profile")

    except Exception as exception:
        print(f"An error occurred: {exception}")
        return HttpResponseRedirect("/user/profile")
