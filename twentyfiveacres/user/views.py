from cryptography.hazmat.primitives.serialization import load_pem_public_key
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from base64 import b64encode, b64decode
import ssl
from django.core.mail import send_mail
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AnonymousUser
from utils.hashing import hashDocument, generateGcmOtp
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from user.viewmodel import generateUserHash, verifyUserDocument
from property.viewmodel import generatePropertyHash
from os import urandom
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


secretKey = urandom(16)

ssl._create_default_https_context = ssl._create_unverified_context
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


from cryptography.exceptions import InvalidSignature

def verify_with_portal_public_key(public_key, message, signature):
    
    if not (isinstance(message, bytes) and isinstance(signature, bytes)):
        print("Error: Message and signature should be bytes-like objects.")
        return None

    
    if not hasattr(public_key, "verify"):
        print("Error: Invalid public key provided.")
        return None

    try:
        
        
        
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return message

    except InvalidSignature:
        print("Error: Signature verification failed.")
        return None

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

from cryptography.hazmat.primitives.padding import PKCS7

def pad_data(data):
    padder = PKCS7(128).padder()  
    padded_data = padder.update(data) + padder.finalize()
    return padded_data

def unpad_data(padded_data):
    unpadder = PKCS7(128).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()
    return data

def encrypt_with_user_sha(user_sha, message):
    message = pad_data(message)
    cipher = Cipher(algorithms.AES(user_sha), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()
    return encryptor.update(message) + encryptor.finalize()

def decrypt_with_user_sha(user_sha, encrypted_message):
    cipher = Cipher(algorithms.AES(user_sha), modes.ECB(), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_message = decryptor.update(encrypted_message) + decryptor.finalize()
    return unpad_data(decrypted_message)

def generate_portal_keys():
    from cryptography.hazmat.primitives.asymmetric import rsa

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key


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

        # Validate roll number against email
        try:
            # Extract the numbers from the email (before "@iiitd.ac.in")
            extractedRollSuffix = email.split("@")[0][-5:]
            # Compare the extracted number with the roll number's last 5 digits
            if extractedRollSuffix != rollNumber[-5:]:
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


def verifyEmail(request):
    if request.method == "POST":
        code = request.POST.get("code")
        rollNumber = request.POST.get("roll_number")
        try:
            user = User.objects.get(rollNumber=rollNumber, verificationCode=code)
            user.verification_code = None
            user.save()
            return HttpResponseRedirect("/user/signin")
        except User.DoesNotExist:
            return USER_INVALID_CODE_OR_ROLLNUMBER_RESPONSE
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
                    return HttpResponseRedirect("/")
            except User.DoesNotExist:
                return USER_INVALID_ROLLNUMBER_RESPONSE
    return render(request, "user/signin_form.html")


def profile(request):
    """
    @desc: renders a page where signed in user can view/update their profile
    """

    if isinstance(request.user, AnonymousUser):
        return USER_SIGNIN_RESPONSE

    user = User.objects.get(username=request.user.username)

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

def sign_with_portal_private_key(private_key, message):
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def handleContract(request, propertyId):
    """
    @desc: handles everything related to a contract
    """

    if isinstance(request.user, AnonymousUser):
        return USER_SIGNIN_RESPONSE

    user = User.objects.get(username=request.user.username)
    user_sha = user.userHash
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
    private_portal_key = "LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JSUV2UUlCQURBTkJna3Foa2lHOXcwQkFRRUZBQVNDQktjd2dnU2pBZ0VBQW9JQkFRQ2pRTk5YZk5ZRTlQTG8KeHRYdjVzRTJwbStjUkZ4YTRGQkFPVWUveUhLR3dQMzNBaUdzaHlycFFnR1prOEhCZm92QlZFVkJKT1lpTVNhVwpVaERRa2dOalc5ZUpVczc1R21UZ1JaR3doTGR1R1lKVFdYcytkOS9QeURlL2ZoSXl6S2UyQzZWUDV2c0RKNnpvCnVSeThnNG05dnNUb1I2WFdPUTQrS2I2NGNMOEZRajg2NldTa0RRdThTYW9HdzRyL1YrTEtWa2pKTnV5UU1tbloKbTQ5WUIxRFp4L3RjZTFJTXFxVkhFNkJOTWV5dExNNitiWTdhN0R0WitLN3hIeDJJdWFHZUpHVitLRUN2dXk4aApTL3U3djMrcjRxbG5HWVFEUDVibmlzTU5tTzA1c0NwMnRzanNSalFUVCtEL2tzUC80NmF4U3BhOFlLZjVUSGpxClgyM2FEQjdaQWdNQkFBRUNnZ0VBQXAyVlJUK1F4aitPYk1CU3lTY3ZUVXJaV3UyVmRUZEcwZUNaRDYrTWRqQTkKWVdtOVZHQk9CYkt6Qjl6Z0s5TjFOY0c5NGs5UENKazAvdytOaVdudGQvZ091ZnFEcW1ZTDI3UUJvNHhjeS96SQpvOEU1UWtUMVp3VFVMOU03UTJrWC9zaXMrMXkrQk16cjdrYVkrVVE2UHJvQnVaNzhQelJtMEFRbk5CbEtWakUwCjkvQjBZS3AwS3VWSW1LdXh4dTlwdDR5ZmpCT0tqUGZraWkzY2tsQ211KytDVXdkSFZqY3ZGRHEydmpkbE9tS1oKMGZzTDJHM0lvWGZqcFZkTTlUVmZhbVpHRE5qZ1J3VDh5TUtEdzFMTVdVc3dNa0prMWNoZU5ydnlCTmY3Z0kvVgpwcHI4aWRYVnFhWUFSenBiUHJZSEc4cFpMc0pIWDRIUXlJWDJlL1g0U1FLQmdRRFVWcUVCMWdvbGZFQlExaU9oCnpWblBJbDNOTHdRNFI4KzlwaUh6ZEwwR0YwekJSdzRmei9kc1VPejZFTWVVMUFUYzZCN1dpVHBXb0dMdFJHMVgKam9HdDZqTm1vcTV1SzBBWEhIMGUvbXluL0xMZWZCalNsWWVZUzdyckQycFZRVzVWZnhCTkQwbGxYWnZFbHlQQwowcjZaYTNvZ2w4YWRCWnFndkplVkpTb0Rad0tCZ1FERTBtR3FOaWk3QXJyM01JM0NoUlhQcEhsdlBjWFA4K3RUCmI5ZUpVTFRUSm1KTGdjWlhhMkp6SVpsOWlXenFyTk1NZzdCSlJSdHl6ZkF1bWU4ajlybUJwOU9nOWhHdmJ6UnYKMmhHSjRqN3VGNlpvamJrNzNvMlNrM3ZLSmEzSEl0ZDZwb3paU1NYanphM0tNRFBqSzl2ejlmb28xRWFndEFPeAprd1lFSDQranZ3S0JnRnlpV21XQnFqV0dTa3k1enh1MGlaeXE0bjgwSnNRaTJBZGxwZVFmSnFPMG9JQ2xiZzBFCjNtMDd0TmEzWVVxVllIVzdNbERuMXpLWmorN3c3ajdIWmQyb2tib1IrTVVKUzFHSjFUQWpVT1hNZ1lBOFpWdmgKYmlGTDBJVGgyY0xONDhPYXhsTEgrMzRrWTJOVmlIMWpFVkcvS0sxMWFXbHhXMjhLTjVzU2RveTdBb0dBRHRlRwpnZDFmcU9xRnlzb2dob0NlcW0vT3NITEtEZXBvM252YWx3STlBSWN1ZGw4czQ3NjNSOU5LemNxbEtmVXFYUkU1CkkrMVFLcElaQUlxZkcra3BCL3Z0MjM5eXlmWHEwRnh6WWlCcmVtelNJYVErU2FONHJZcnRsTXJPbGV1c3NCVUwKSGYrRUdlK1NvV0tOSng1UmtjNEV0VHQ4ci9XakthcmFrMGtGL2VVQ2dZRUF2ZkxrT2NwbVU0cjFhQjM1eHh6eAowVTI2OG9ZaGZOczNFRGJMQVRVSlZPK0tHVkduUDc0NmJGRFVIK3AyQ3pnY2lwbmpCeHdHQzJ6RE4xbVBmemV4ClQ5dW9HZTVhZkJIQVdWMkhJQVJSRWlUZy9vSVEyYVU2cUFNY0VqYTROWGdCMUZVSmZMdEs2WnZIeDg3b3kwL1YKZERYZnROWm1oVVBEQzZWVk9neFFHdWM9Ci0tLS0tRU5EIFBSSVZBVEUgS0VZLS0tLS0K"
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
        contract_hash = sellerContract.contractHashIdentifier
        signature = sign_with_portal_private_key(private_portal_key, contract_hash)
        encrypted_signature = encrypt_with_user_sha(user_sha, signature)

        #  now need to mail these both things contract hash and encrypted signature to the user
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
        contract_hash = buyerContract.contractHashIdentifier
        signature = sign_with_portal_private_key(private_portal_key, contract_hash)
        encrypted_signature = encrypt_with_user_sha(user_sha, signature)

        #  now need to mail these both things contract hash and encrypted signature to the user
        
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

    # check if the user is authenticated
    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("../../")

    user = User.objects.get(username=request.user.username)

    # check whether propertyId provided is valid or not
    try:
        propertyObj = Property.objects.get(pk=propertyId)
    except ObjectDoesNotExist:
        return PROPERTY_DOES_NOT_EXIST_RESPONSE

    # check if the user has the right to change ownership for this property
    if propertyObj.owner != user:
        return USER_NOT_OWNER_RESPONSE

    # check proof of identity
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

    # Update ownership document if it is not None
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
    if request.method == "POST":
        verification_text = request.POST.get('verification_string')
        verification_text_bytes = base64.b64decode(verification_text)

        
        contract_sha_digest = base64.b64decode(request.POST.get('contract_sha'))

        # use environemnt variable baad mein 
        portal_public_key_encoded = "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQklqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FROEFNSUlCQ2dLQ0FRRUF2UEplbVJtOW90djJJYUR0NEpDaAphN0tZQW1CQk0vV1lMMk5oMWR6REltNmcyVFB4MkpOd1I3cSsyeGhEajVRNlArVXkwUVJqemhEZG5sTkVOa3htCkJ5c0Q4Tlk0SmN3cVZ6QksxUENGdjAzSG1LOG0rUVRaTEUwNW1ybFdjczd3d0FaMXRUQlhBeUx2QjU3SWduNmsKTi9aaENhU20rSnlHRHA3SU9hRkdLOTlwNUVsQWNwZkRRVW0yUGZNU1ZBYW1rMVVjeEZqTE83M1JTSnJUUFU4UwpZSWpkNDRtd3VySzFtUHcxWENHR0pKT0RzQlFQVUl1aGg4UlpIbVdkVnZ1MHBoRVZwQ0Q0bktCQjEyclZMT09FCjhBS2JUenVWclJ0MkZsbXNQZXhKcXZtaG1LYURFdmJxcXNVbTQ5TVJTemR3Z3QwUE11YkcyQ1IrTCtNT0pKOVUKdXdJREFRQUIKLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0tCg=="
        portal_public_key_bytes = base64.b64decode(portal_public_key_encoded)
        portal_public_key = load_pem_public_key(portal_public_key_bytes, backend=default_backend())
        
        
        username = request.POST.get('user_identifier')
        user = User.objects.get(username=username)
        
        user_sha = base64.b64decode(user.userHash)

        
        decrypted_signature = decrypt_with_user_sha(user_sha, verification_text_bytes)

        
        verified_contract_sha = verify_with_portal_public_key(portal_public_key, contract_sha_digest, decrypted_signature)

        
        if verified_contract_sha == contract_sha_digest:
            verification_result = "sanctioned"
        else:
            verification_result = "not_sanctioned"
        print(verification_result)
        context = {'verification_result': verification_result}
        
        
        return HttpResponseRedirect("/user/profile")

    return HttpResponseRedirect("/user/profile")