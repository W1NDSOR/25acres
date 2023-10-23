from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AnonymousUser
from utils.hashing import hashDocument
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from user.viewmodel import generateUserHash, verifyUserDocument
from property.viewmodel import generatePropertyHash
from os import urandom
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.backends import default_backend
from base64 import b64decode
from utils.mails import generateGcmOtp, sendMail
from contract.viewmodel import (
    generateUserPropertyContractHash,
    getAbstractContractArray,
    AbstractContract,
    ContractStages,
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
    USER_SIGNIN_WITHOUT_VERIFICATION_REPONSE,
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
import requests
from rest_framework_simplejwt.tokens import RefreshToken

from twentyfiveacres.settings import basic_url

secretKey = urandom(16)


def authenticateUser(token):
    try:
        url=basic_url+"auth/token/verify/"
        data={"token":token}
        response=requests.post(url,json=data)
        print(response.status_code)
        if response.status_code==200:
            return True
            
        return False

    except Exception as e:
        print('User not authenticated')
        return False

def index(request):
    try:
        if not authenticateUser(request.session['access_token']):
            return redirect('/signin')

    except Exception as e:
        print('User not authenticated')
        return redirect('/signin')




def verifyEmail(request):
    if request.method == "POST":
        code = request.POST.get("code")
        rollNumber = request.POST.get("roll_number")
        url = basic_url + "auth/verifyEmail/"
        data = {"roll_number": rollNumber, "code": code}
        response = requests.get(url, json=data)
        response = response.json()
        print(response)
        if response["status"]:
            return HttpResponseRedirect("/user/signin")
        else:
            messages.success(request, response["message"])
        # try:
        #     user = User.objects.get(rollNumber=rollNumber, verificationCode=code)
        #     user.verificationCode = None
        #     user.save()
        #     return HttpResponseRedirect("/user/signin")
        # except User.DoesNotExist:
        #     return USER_INVALID_CODE_OR_ROLLNUMBER_RESPONSE
    return render(request, "user/verify_email.html")


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
            extracted_roll_suffix = email.split("@")[0][-5:]
            if extracted_roll_suffix != rollNumber[-5:]:
                return render(request, "user/signup_form.html", {
                    "error": "Your email ID and roll number don't match!"
                })
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
            url = basic_url + "auth/register/"
            data = {
                "username": username,
                "email": email,
                "password": make_password(password),
                "firstname": firstName,
                "lastname": lastName,
                "rollNumber": rollNumber,
                "documentHash": documentHash,
                # "verificationCode": verificationCode,
            }
            response = requests.post(url, json=data)
            response = response.json()
            print(response)

            if response["status"]:
                messages.error(request, response["message"])
                return HttpResponseRedirect(reverse("verify_email"))
            # verificationCode = generateGcmOtp(secretKey, rollNumber.encode())
            # user = User.objects.create(
            #     username=username,
            #     email=email,
            #     rollNumber=rollNumber,
            #     password=make_password(password),
            #     first_name=firstName,
            #     last_name=lastName,
            #     documentHash=documentHash,
            #     userHash=generateUserHash(username, rollNumber, email),
            #     verificationCode=verificationCode,
            # )
    return render(request, "user/signup_form.html")


def signin(request):
    """
    @desc: renders a form for signing up new user
    """
    if request.method == "POST":
        userFields = request.POST
        rollNumber = userFields.get("roll_number")
        password = userFields.get("password")
        print('user info: ',rollNumber,password)
        if rollNumber=='':
            messages.error(request, 'rollNumber cannot be empty')
            return render(request,'user/signin_form.html')
        if password=='':
            messages.error(request, 'Password cannot be empty')
            return render(request,'user/signin_form.html')
        
        url = basic_url + "auth/signin/"
        data = {"roll_number": rollNumber, "password": password}

        response = requests.post(url, json=data)
        response = response.json()
        print(response)
        if response["status"]:
            print(response['message'])
            print(response['data']['roll_number'])
            request.session['roll_number']=response['data']['roll_number']
            request.session['username']=response['data']['username']
            request.session['access_token']=response['data']['token']['access']
            request.session['refresh_token']=response['data']['token']['refresh']
            return HttpResponseRedirect("/")
        else:
            messages.success(request, response["message"])
    return render(request, "user/signin_form.html")


# # Profile and Property


def profile(request):
    """
    Django view for rendering user profile template.
    """
    
    if request.method == "GET":
        return render(request, "user/profile.html")
    
    elif request.method == "POST" and request.POST.get("action") == "profileDetailButton":
        user = User.objects.get(username=request.user.username)
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.save()
        return HttpResponseRedirect("/user/profile/")
    
    return render(request, "user/profile.html")

# def deleteProperty(request, propertyId):
#     """
#     @desc: deletes property with propertyId if user is the owner of the property
#     @params {int} propertyId: Id of the property to be deleted
#     """

#     if isinstance(request.user, AnonymousUser):
#         return USER_SIGNIN_RESPONSE

#     user = User.objects.get(username=request.user.username)
#     try:
#         property = Property.objects.get(propertyId=propertyId)
#         if property.owner == user:
#             property.delete()
#             return HttpResponseRedirect("/")
#         else:
#             return USER_NOT_OWNER_RESPONSE
#     except ObjectDoesNotExist:
#         return PROPERTY_DOES_NOT_EXIST_RESPONSE


# def handleContract(request, propertyId):
#     """
#     @desc: handles everything related to a contract
#     """

#     if isinstance(request.user, AnonymousUser):
#         return USER_SIGNIN_RESPONSE
#     user = User.objects.get(username=request.user.username)

#     try:
#         property = Property.objects.get(propertyId=propertyId)
#     except ObjectDoesNotExist:
#         return PROPERTY_DOES_NOT_EXIST_RESPONSE

#     if property.owner != user and property.bidder != user:
#         return USER_NOT_BIDDER_NOR_OWNER_RESPONSE

#     try:
#         abstractContract = AbstractContract(Contract.objects.get(property=propertyId))
#     except ObjectDoesNotExist:
#         abstractContract = AbstractContract(None)

#     # hardcoded the private key for the portal
#     if (
#         abstractContract.currentStage == ContractStages.SELLER.value
#         and property.owner == user
#     ):
#         sellerContract = SellerContract.objects.create(
#             property=property,
#             seller=user,
#             contractHashIdentifier=generateUserPropertyContractHash(user, property),
#             contractAddress=None,
#         )
#         sellerContract.save()
#         contract = Contract.objects.create(
#             property=property,
#             sellerContract=sellerContract,
#         )
#         contract.save()
#         # contract hash
#         contractHash = sellerContract.contractHashIdentifier
#         signature = signWithPortalPrivateKey(PORTAL_PRIVATE_KEY, contractHash)
#         encryptedSignature = encryptWithUserSha(user.userHash, signature)
#         sendMail(
#             subject="Details for your property",
#             message=f"""Here your details for property
# - Property Id: {property.propertyId}
# - Property Title: {property.title}
# - Contract hash: {contractHash}
# - Encypted signature: {encryptedSignature}""",
#             recipientEmails=[user.email],
#         )
#         # TODO: now need to mail these both things `contractHash` and `encryptedSignature` to the user

#         return HttpResponseRedirect("/user/profile")

#     if (
#         abstractContract.currentStage == ContractStages.BUYER.value
#         and property.bidder == user
#     ):
#         buyerContract = BuyerContract.objects.create(
#             property=property,
#             buyer=user,
#             contractHashIdentifier=generateUserPropertyContractHash(user, property),
#             contractAddress=None,
#         )
#         buyerContract.save()
#         contractHash = buyerContract.contractHashIdentifier
#         signature = signWithPortalPrivateKey(PORTAL_PRIVATE_KEY, contractHash)
#         encryptedSignature = encryptWithUserSha(user.userHash, signature)
#         # TODO: now need to mail these both things `contractHash` and `encryptedSignature` to the user

#         abstractContract.contract.buyerContract = buyerContract
#         abstractContract.contract.save()
#         if property.status in ("for_sell", "For Sell"):
#             property.status = "Sold"
#         elif property.status in ("for_rent", "For Rent"):
#             property.status = "Rented"
#         property.save()
#         return HttpResponseRedirect("/user/profile")

#     return TRESPASSING_RESPONSE


# def changeOwnership(request, propertyId):
#     if request.method != "POST":
#         TRESPASSING_RESPONSE

#     if isinstance(request.user, AnonymousUser):
#         return HttpResponseRedirect("../../")

#     user = User.objects.get(username=request.user.username)
#     try:
#         propertyObj = Property.objects.get(pk=propertyId)
#     except ObjectDoesNotExist:
#         return PROPERTY_DOES_NOT_EXIST_RESPONSE

#     # Won't occur
#     if propertyObj.owner != user:
#         return USER_NOT_OWNER_RESPONSE

#     # check proof of identity
#     proofOfIdentity = (
#         request.FILES[f"proof_identity_{propertyId}"].read()
#         if f"proof_identity_{propertyId}" in request.FILES
#         else None
#     )
#     if not proofOfIdentity or not verifyUserDocument(user, proofOfIdentity):
#         return USER_DOCUMENT_HASH_MISMATCH_RESPONSE

#     ownershipDocumentHash = (
#         hashDocument(request.FILES[f"ownership_document_{propertyId}"].read())
#         if f"ownership_document_{propertyId}" in request.FILES
#         else None
#     )

#     if ownershipDocumentHash is None:
#         return PROPERTY_OWNERSHIP_DOCUMENT_MISSING_RESPONSE

#     # Update ownership document if it is not None (it cannot be None, cause field required while adding property)
#     ownershipDocumentHash = ownershipDocumentHash
#     propertyObj.ownershipDocumentHash = ownershipDocumentHash
#     propertyObj.propertyHashIdentifier = generatePropertyHash(
#         ownershipDocumentHash,
#         propertyObj.title,
#         propertyObj.description,
#         propertyObj.price,
#         propertyObj.bedrooms,
#         propertyObj.bathrooms,
#         propertyObj.area,
#         propertyObj.status,
#         propertyObj.location.name,
#         propertyObj.availabilityDate,
#     )
#     propertyObj.save()
#     return HttpResponseRedirect("/user/profile")


# def verifyContract(request):
#     try:
#         if request.method == "POST":
#             verificationText = request.POST.get("verification_string")
#             verificationTextBytes = b64decode(verificationText)
#             contractShaDigest = b64decode(request.POST.get("contract_sha"))

#             # TODO: replace this logic with environment variable
#             portalPublicKeyBytes = b64decode(PORTAL_PUBLIC_ENCODED_KEY)
#             portalPublicKey = load_pem_public_key(
#                 portalPublicKeyBytes, backend=default_backend()
#             )

#             username = request.POST.get("user_identifier")
#             user = User.objects.get(username=username)
#             userSha = b64decode(user.userHash)

#             decryptedSignature = decryptWithUserSha(userSha, verificationTextBytes)
#             verifiedContractSha = verifyWithPortalPublicKey(
#                 portalPublicKey, contractShaDigest, decryptedSignature
#             )

#             if verifiedContractSha == contractShaDigest:
#                 verification_result = "sanctioned"
#             else:
#                 verification_result = "not_sanctioned"

#             print(verification_result)
#             context = {"verification_result": verification_result}

#     except Exception as exception:
#         print(f"An error occurred: {exception}")

#     return HttpResponseRedirect("/user/profile")
