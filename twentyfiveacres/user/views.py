import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.hashes import SHA256, Hash
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend

from cryptography.hazmat.primitives import serialization, padding
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.hashes import SHA256
from base64 import b64decode
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from base64 import b64decode
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key
from cryptography.hazmat.primitives.asymmetric.padding import PSS, MGF1
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import ECB
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import padding
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AnonymousUser
from utils.hashing import hashDocument
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.http import HttpResponse
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
    Transaction,
)
from utils.crypto import (
    sign_data,
    verify_contract
)

secretKey = urandom(16)


def verifyEmail(request):
    if request.method == "POST":
        code = request.POST.get("code")
        rollNumber = request.POST.get("roll_number")
        try:
            user = User.objects.get(rollNumber=rollNumber, verificationCode=code)
            user.verificationCode = None
            user.save()
            return HttpResponseRedirect("/user/signin")
        except User.DoesNotExist:
            return USER_INVALID_CODE_OR_ROLLNUMBER_RESPONSE
    return render(request, "user/verify_email.html")

# def signup(request):
#     email = request.session.get('eKYC_email')
    
#     if request.method == "POST":
#         # ... (same as your provided code)
        
#         if (username and email and password and firstName and lastName and rollNumber and documentHash):
#             # ... (same as your provided code)
            
#             del request.session['eKYC_email']  # clear email from session after successful signup
#             return HttpResponseRedirect("/user/verify_email")
#     else:
#         return render(request, "user/signup_form.html", {'email': email})

def signup(request):
    """
    @desc: renders a form for signing up new user
    """
    email = request.session.get('eKYC_email')
    if email is None:
        messages.error(request, "Please complete eKYC verification first.")
        return redirect("/user/eKYC")
    
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
                # TODO: remember to uncomment what below
                # return USER_EMAIL_ROLLNUMBER_MISMATCH_RESPONSE
                pass
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
            transaction = Transaction.objects.create(
                user=user,
                withPortal=True,
                other=None,
                amount=1000000000,
                credit=True,
                debit=False,
            )
            transaction.save()
            sendMail(
                subject="Welcome to 25acres",
                message=f"Your verification code is {verificationCode}",
                recipientEmails=[email],
            )
            del request.session['eKYC_email']  # clear email from session after successful signup
            return HttpResponseRedirect("/user/verify_email")
    else:
        return render(request, "user/signup_form.html", {'email': email})
    return render(request, "user/signup_form.html")



import requests
from django.shortcuts import render, redirect
from django.contrib import messages

from django.shortcuts import redirect

def eKYC(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Define the API endpoint for eKYC verification
        api_endpoint = "https://192.168.3.39:5000/kyc"
        
        # Prepare the data for the POST request
        data = {
            "email": email,
            "password": password
        }
        
        try:
            # Make the POST request to the eKYC API
            response = requests.post(api_endpoint, json=data, verify=False)
            response_data = response.json()
            
            # Check the response from the eKYC API
            if response_data.get("status") == "success":  # assuming "success" indicates a successful verification
                print("lessgo")
                # If verification is successful, set session variable and redirect to signup
                request.session['eKYC_email'] = email
                return redirect('/user/signup')
                
            else:
                # If verification fails, return an error message
                context = {
                    "error_message": "eKYC verification failed. Please try again."
                }
                return render(request, 'user/eKYC.html', context)
                
        except Exception as e:
            # Log the exception for debugging purposes
            print("An error occurred:", str(e))
            context = {
                "error_message": "An internal error occurred. Please try again later."
            }
            return render(request, 'user/eKYC.html', context)
    
    return render(request, 'user/eKYC.html')


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
                if user.verificationCode is not None:
                    return USER_SIGNIN_WITHOUT_VERIFICATION_REPONSE
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
    @desc: renders user profile
    """

    if isinstance(request.user, AnonymousUser):
        return USER_SIGNIN_RESPONSE

    user = User.objects.get(username=request.user.username)

    properties = Property.objects.filter(owner=user)
    contracts = getAbstractContractArray(properties)
    propertyBidings = Property.objects.filter(Q(bidder=user) & ~Q(owner=user))
    propertyBidingsContracts = getAbstractContractArray(propertyBidings)
    pastProperties = Property.objects.filter(Q(originalOwner=user) & ~Q(owner=user))

    context = {
        "username": user.username,
        "roll_number": user.rollNumber,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "wallet": user.wallet,
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

    # check proof of identity
    proofOfIdentity = (
        request.FILES[f"proof_identity_{propertyId}"].read()
        if f"proof_identity_{propertyId}" in request.FILES
        else None
    )
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

from base64 import b64encode

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
        abstractContract = AbstractContract(Contract.objects.get(property=propertyId))
    except ObjectDoesNotExist:
        abstractContract = AbstractContract(None)

    if (
        abstractContract.currentStage == ContractStages.SELLER.value
        and property.owner == user
    ):
        sellerContract = SellerContract.objects.create(
            property=property,
            seller=user,
            contractHashIdentifier=generateUserPropertyContractHash(user, property),
            contractAddress=None,
        )
        sellerContract.save()
        contract = Contract.objects.create(
            property=property,
            sellerContract=sellerContract,
        )
        contract.save()
        property.listed = False
        property.save()
        # contract hash
        print("HERE IS WHAT YOU ARE LOOKING FOR")
        contractHash = sellerContract.contractHashIdentifier
        contract_hash = contractHash.encode('utf-8')
        signature = sign_data(contract_hash)
        signature_str = b64encode(signature).decode('utf-8')
        sendMail(
            subject="Details for your property",
            message=f"""Here your details for property
        - Property Id: {property.propertyId}
        - Property Title: {property.title}
        - Contract hash: {contractHash}
        - Encypted signature: {signature_str}""",
            recipientEmails=[user.email],
        )
        print("Contract sent to the email id....")

        # TODO: now need to mail these both things `contractHash` and `encryptedSignature` to the user

        return HttpResponseRedirect("/user/profile")

    if (
        abstractContract.currentStage == ContractStages.BUYER.value
        and property.bidder == user
    ):
        buyerContract = BuyerContract.objects.create(
            property=property,
            buyer=user,
            contractHashIdentifier=generateUserPropertyContractHash(user, property),
            contractAddress=None,
        )
        buyerContract.save()
        contractHash = buyerContract.contractHashIdentifier
        contract_hash = contractHash.encode('utf-8')
        signature = sign_data(contract_hash)
        signature_str = b64encode(signature).decode('utf-8')

        sendMail(
            subject="Details for your property",
            message=f"""Here your details for property
        - Property Id: {property.propertyId}
        - Property Title: {property.title}
        - Contract hash: {contractHash}
        - Encypted signature: {signature_str}""",
            recipientEmails=[user.email],
        )
        print("Contract sent to the email id....")
        # TODO: now need to mail these both things `contractHash` and `encryptedSignature` to the user

        abstractContract.contract.buyerContract = buyerContract
        abstractContract.contract.save()
        sendMail(
            subject="Contract Verfied",
            message="Your property buying contract with the portal is finalized; Kindly proceed to payment",
            recipientEmails=[user.email],
        )
        print("Send email here as well ffff")
        return HttpResponseRedirect("/user/profile")

    return TRESPASSING_RESPONSE

def verifyContract(request):
    if request.method == "POST":
        try:
            verificationText = request.POST.get("verification_string")
            signature = b64decode(verificationText)
            contractSha = request.POST.get("contract_sha")
            is_valid = verify_contract(contractSha, signature)

            verification_result = "sanctioned" if is_valid else "not_sanctioned"
            print(verification_result)
            context = {"verification_result": verification_result}
# TO DO: i want to display the result to the front end someone please do it i am too tired make sure that if the reponse is sanctioned only then show sanctioned rest in all cases show not sanctioned even if there is some error 
        except Exception as exception:
            print(f"An error occurred: {exception}")

    return HttpResponseRedirect("/user/profile")

def process_payment(request):
    if request.method == "POST":
        property_id = request.POST.get("property_id")
        print(property_id)
        if property_id:
            return HttpResponseRedirect(f"/transaction/paymentGateway/{property_id}/")
        else:
            return HttpResponse("Property ID is missing")
    else:
        return HttpResponse("Invalid request")
