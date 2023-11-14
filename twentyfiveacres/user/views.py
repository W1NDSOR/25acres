from datetime import datetime, date
from django.contrib import messages
from requests import post as requestsPost
from base64 import b64decode
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from utils.hashing import hashDocument
from django.http import HttpResponse
from django.db.models import Q
from user.viewmodel import generateUserHash, verifyUserDocument
from property.viewmodel import generatePropertyHash
from os import urandom
from requests.exceptions import ConnectTimeout
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
    USER_INVALID_EMAIL_FORMAT_RESPONSE,
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
    Transaction,
)
from utils.crypto import sign_data, verify_contract


def verifyEmail(request):
    context = {}
    if request.method == "POST":
        code = request.POST.get("code")
        rollNumber = request.POST.get("roll_number")
        try:
            user = User.objects.get(rollNumber=rollNumber, verificationCode=code)
            user.verificationCode = None
            user.save()
            return HttpResponseRedirect("/user/signin")
        except User.DoesNotExist:
            context["error"] = "Invalid verification code or rollnumber"
            return render(request, "user/verify_email.html", context)
    return render(request, "user/verify_email.html")


def signup(request):
    email = request.session.get("eKYC_email")
    if email is None:
        messages.error(request, "Please complete eKYC verification first.")
        return redirect("/user/eKYC")

    if request.method == "POST":
        try:
            userFields = request.POST
            username = userFields.get("user_name")
            rollNumber = userFields.get("roll_number")
            email = userFields.get("email")
            password = userFields.get("password")
            confirmPassword = userFields.get("confirm_password")
            firstName = userFields.get("first_name")
            lastName = userFields.get("last_name")

            # Roll No and Email Validation
            try:
                extractedRollSuffix = email.split("@")[0][-5:]
                if extractedRollSuffix != rollNumber[-5:]:
                    # TODO: remember to uncomment what below
                    return USER_EMAIL_ROLLNUMBER_MISMATCH_RESPONSE    
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
                and confirmPassword
                and firstName
                and lastName
                and rollNumber
                and documentHash
                and password == confirmPassword
            ):
                secretKey = urandom(16)
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
                print(verificationCode)
                transaction.save()
                sendMail(
                    subject="Welcome to 25acres",
                    message=f"Your verification code is {verificationCode}",
                    recipientEmails=[email],
                )
                del request.session[
                    "eKYC_email"
                ]  # clear email from session after successful signup
                return HttpResponseRedirect("/user/verify_email")
        except IntegrityError:
            messages.error(
                request,
                'User already exists. Please choose a roll number or go back and <a href="/user/signin"> Signin.</a>',
            )
            return redirect("/user/signup")

    else:
        return render(request, "user/signup_form.html", {"email": email})
    return render(request, "user/signup_form.html")


def eKYC(request):
    context = {}
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Check if user with the given email already exists
        user_exists = User.objects.filter(email=email).exists()

        if user_exists:
            context[
                "error_message"
            ] = "User with this email already exists. Please proceed to <a href='/user/signin'>Signin.</a>"
            return render(
                request, "user/eKYC.html", context
            )  # Render the template with the error message
        if email[-11:] != "iiitd.ac.in":
            context[
                "error_message"
            ] = "We are currently only accepting IIITD email addresses. Please try again with your IIITD email address."
            return render(
                request, "user/eKYC.html", context
            )  # Render the template with the error message
        # Define the API endpoint for eKYC verification
        api_endpoint = "https://192.168.3.39:5000/kyc"

        # Prepare the data for the POST request
        data = {"email": email, "password": password}

        try:
            # Make the POST request to the eKYC API
            response = requestsPost(api_endpoint, json=data, verify=False)
            response_data = response.json()

            # Check the response from the eKYC API
            if (
                response_data.get("status") == "success" 
                # response_data.get("status") != "success"    # Testing purpose: Remove eKYC verification 
            ):  # assuming "success" indicates a successful verification
                request.session["eKYC_email"] = email
                return redirect("/user/signup")

            else:
                # If verification fails, return an error message
                context[
                    "error_message"
                ] = "eKYC verification failed. Please check your credentials and try again."

        except ConnectTimeout:
            context[
                "error_message"
            ] = "Connection timeout occurred. Please ensure you are connected to the VPN and try again."

        except Exception as e:
            print("An error occurred:", str(e))
            context[
                "error_message"
            ] = "An internal error occurred. Please try again later."

    return render(request, "user/eKYC.html", context)


def signin(request):
    return render(request, "user/signin_form.html", context={"error_message": request.GET.get("message")})

def signinWithPassword(request):
    if request.method == "POST":
        userFields = request.POST
        rollNumber = userFields.get("roll_number")
        password = userFields.get("password")
        if rollNumber and password:
            try:
                user = User.objects.get(rollNumber=rollNumber)
                if user.verificationCode is None:
                    salt = user.password.split("$")[2]
                    if user.password == make_password(password, salt=salt):
                        login(request, user)
                        return redirect("/?message=You are logged in")
                    else: return redirect("/user/signin?message=Invalid password")
                else: redirect("/user/verify_email")
            except: return redirect("/user/signin?message=Invalid roll number")
        else: return redirect("/user/signin?message=Please enter both roll numuber and password")
    return redirect("/user/signin")


def signinWithOTP(request):
    if request.method == "POST":
        userFields = request.POST
        rollNumber = userFields.get("roll_number")
        otp = userFields.get("otp")
        otpSent = userFields.get("otp_sent")
        print("otp_sent from request: ", otpSent)
        if "send_otp" in request.POST:
            print("received the request to send the otp")
            try:
                user = User.objects.get(rollNumber=rollNumber)
                secretKey = urandom(16)
                otp = generateGcmOtp(secretKey, rollNumber.encode())
                sendMail(
                    subject="OTP for login",
                    message=f"""Here is your OTP for login: {otp}""",
                    recipientEmails=[user.email],
                )
                print("OTP sent to the email id....")
                user.verificationCode = otp
                user.save()
                messages.success(request, "OTP sent to your email.")
                print(otp)
                print(user.verificationCode)
                return render(request, "user/signin_form.html", {"otp_sent": "1"})
            except: return redirect("/user/signin?message=Invalid roll number")

        if otp:
            print("are we even reachinghere or not")
            try:
                user = User.objects.get(rollNumber=rollNumber)
                print(otp)
                print(user.verificationCode)
                if otp == user.verificationCode:  
                    login(request, user)
                    user.verificationCode = None
                    user.save()
                    return redirect("/user/signin?message=You are logged in")
                else:
                    return redirect("/user/signin?message=Invalid OTP")
            except: return redirect("/user/signin?message=Invalid roll number")
    return HttpResponseRedirect("/user/signin")


# Profile and Property
def pay_monthly():
    # Get all rented properties
    rented_properties = Property.objects.filter(status="Rented")

    for property in rented_properties:
        # Calculate the months passed since the availabilityDate
        today = date.today()
        today = datetime.strptime(str("2023-12-31"), "%Y-%m-%d").date()
        delta = today - property.availabilityDate
        months_passed = delta.days // 30

        months_remaining = property.rent_duration - months_passed
        # print(f"Property title: {property.title}, availability date:{property.availabilityDate} Rent Duration: {property.rent_duration}, Status: {property.status}, months remaining: {months_remaining}")
        if months_remaining <= 0:
            property.monthsRemaining = 0
            property.owner = property.originalOwner
            property.status = "For Rent"
        else:
            property.monthsRemaining = months_remaining

        property.save()


def profile(request):
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
    pay_monthly()
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
        contract_hash = contractHash.encode("utf-8")
        signature = sign_data(contract_hash)
        signature_str = b64encode(signature).decode("utf-8")
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
        contract_hash = contractHash.encode("utf-8")
        signature = sign_data(contract_hash)
        signature_str = b64encode(signature).decode("utf-8")

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
            # Handle the file upload
            if "ownership_document" in request.FILES:
                ownershipDocument = request.FILES["ownership_document"]
                ownershipDocumentHash = ownershipDocument.read()  # Generate hash from the uploaded document

                try:
                    # Retrieve the existing property
                    property = Property.objects.get(propertyId=property_id)

                    # Update the ownership document hash
                    property.ownershipDocumentHash = ownershipDocumentHash

                    # Generate a new property hash identifier
                    property.propertyHashIdentifier = generatePropertyHash(
                        ownershipDocumentHash,
                        property.title,
                        property.description,
                        property.price,
                        property.bedrooms,
                        property.bathrooms,
                        property.area,
                        property.status,
                        property.location.name,
                        property.availabilityDate,
                    )

                    # Save the updated property
                    property.save()

                    # Redirect to the payment gateway
                    return HttpResponseRedirect(f"/transaction/paymentGateway/{property_id}/")

                except Property.DoesNotExist:
                    return HttpResponse("Property not found")
                except Exception as e:
                    print(f"Exception occurred: {e}")
                    return HttpResponse("An error occurred while processing the document")

            else:
                return HttpResponse("Ownership document is missing")

        else:
            return HttpResponse("Property ID is missing")
    else:
        return HttpResponse("Invalid request")
