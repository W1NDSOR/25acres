from django.http import JsonResponse
from django.contrib.auth import login
from base64 import b64decode
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AnonymousUser
from utils.hashing import hashDocument
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from user.viewmodel import generateUserHash, verifyUserDocument
from property.viewmodel import generatePropertyHash
from os import urandom
from os import urandom
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.backends import default_backend
from django.contrib.auth import authenticate, login
from django.shortcuts import render
from utils.mails import generateGcmOtp, sendMail
from contract.viewmodel import generateUserPropertyContractHash
from restapi.models import User, Property, Contract, SellerContract, BuyerContract
from utils.crypto import (
    verifyWithPortalPublicKey,
    encryptWithUserSha,
    decryptWithUserSha,
    signWithPortalPrivateKey,
    PORTAL_PRIVATE_KEY,
    PORTAL_PUBLIC_ENCODED_KEY,
)
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
from restapi.models import (
    User,
    Property,
    Contract,
    SellerContract,
    BuyerContract,
)

secretKey = urandom(16)

from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class VerifyEmailView(APIView):
    def post(self, request):
        code = request.data.get("code")
        rollNumber = request.data.get("roll_number")
        try:
            user = User.objects.get(rollNumber=rollNumber, verificationCode=code)
            user.verificationCode = None
            user.save()
            return Response(
                {"message": "Successfully verified."}, status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                USER_INVALID_CODE_OR_ROLLNUMBER_RESPONSE,
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get(self, request):
        # This is just for demonstration, generally API endpoints don't serve templates
        return render(request, "user/verify_email.html")

class SignupView(APIView):
    def post(self, request):
        userFields = request.POST
        username = userFields.get("user_name")
        rollNumber = userFields.get("roll_number")
        email = userFields.get("email")
        password = userFields.get("password")
        firstName = userFields.get("first_name")
        lastName = userFields.get("last_name")

        print(f"{username} {rollNumber} {email} {password} {firstName} {lastName}")

        # Roll No and Email Validation
        try:
            extractedRollSuffix = email.split("@")[0][-5:]
            if extractedRollSuffix != rollNumber[-5:]:
                pass
                # return Response(USER_EMAIL_ROLLNUMBER_MISMATCH_RESPONSE, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(
                USER_INVALID_EMAIL_FORMAT_RESPONSE, status=status.HTTP_400_BAD_REQUEST
            )

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
            sendMail(
                subject="Welcome to 25acres",
                message=f"Your verification code is {verificationCode}",
                recipientEmails=[email],
            )

            return Response(
                {"message": "Signup successful. Verify your email."},
                status=status.HTTP_201_CREATED,
            )


class SigninView(APIView):
    def post(self, request):
        user_fields = request.data  # Assuming you're sending data in JSON format
        roll_number = user_fields.get("roll_number")
        password = user_fields.get("password")

        if roll_number and password:
            try:
                user = authenticate(request, username=roll_number, password=password)

                if user:
                    if user.verificationCode is not None:
                        return Response(
                            USER_SIGNIN_WITHOUT_VERIFICATION_REPONSE,
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    login(request, user)
                    return Response(
                        {"message": "Successfully signed in."},
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        USER_INVALID_ROLLNUMBER_RESPONSE,
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            except User.DoesNotExist:
                return Response(
                    USER_INVALID_ROLLNUMBER_RESPONSE, status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            {"message": "Invalid input data."}, status=status.HTTP_400_BAD_REQUEST
        )


class ProfileView(APIView):
    def get(self, request):
        if isinstance(request.user, AnonymousUser):
            return Response(USER_SIGNIN_RESPONSE, status=status.HTTP_401_UNAUTHORIZED)

        user = request.user
        num_properties = Property.objects.filter(owner=user).count()

        properties = Property.objects.filter(
            owner=user, status__in=["for_sell", "For Sell", "for_rent", "For Rent"]
        )

        # You may need to implement the getAbstractContractArray function
        # to retrieve contract data for properties.
        contracts = []  # Implement this based on your logic

        property_bidings = Property.objects.filter(
            bidder=user, status__in=["for_sell", "For Sell", "for_rent", "For Rent"]
        )

        # You may need to implement the getAbstractContractArray function
        # to retrieve contract data for property bidings.
        property_bidings_contracts = []  # Implement this based on your logic

        past_properties = Property.objects.filter(
            Q(owner=user) | Q(bidder=user), status__in=["Sold", "Rented"]
        )

        data = {
            "username": user.username,
            "roll_number": user.rollNumber,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "properties_count": num_properties,
            "properties": [
                {
                    "property_id": property.propertyId,
                    "title": property.title,
                    "status": property.status,
                    # Add more property fields as needed
                }
                for property in properties
            ],
            "contracts": contracts,
            "property_bidings": [
                {
                    "property_id": property.propertyId,
                    "title": property.title,
                    "status": property.status,
                    # Add more property fields as needed
                }
                for property in property_bidings
            ],
            "property_bidings_contracts": property_bidings_contracts,
            "past_properties": [
                {
                    "property_id": property.propertyId,
                    "title": property.title,
                    "status": property.status,
                    # Add more property fields as needed
                }
                for property in past_properties
            ],
        }

        return Response(data, status=status.HTTP_200_OK)


class DeletePropertyView(APIView):
    def delete(self, request, property_id):
        if isinstance(request.user, AnonymousUser):
            return Response(USER_SIGNIN_RESPONSE, status=status.HTTP_401_UNAUTHORIZED)

        user = request.user
        try:
            property = Property.objects.get(propertyId=property_id)
            if property.owner == user:
                property.delete()
                return Response(
                    {"message": "Property deleted successfully."},
                    status=status.HTTP_204_NO_CONTENT,
                )
            else:
                return Response(
                    USER_NOT_OWNER_RESPONSE, status=status.HTTP_403_FORBIDDEN
                )
        except ObjectDoesNotExist:
            return Response(
                PROPERTY_DOES_NOT_EXIST_RESPONSE, status=status.HTTP_404_NOT_FOUND
            )


class HandleContractView(APIView):
    def post(self, request, property_id):
        if isinstance(request.user, AnonymousUser):
            return Response(USER_SIGNIN_RESPONSE, status=status.HTTP_401_UNAUTHORIZED)

        user = request.user
        try:
            property = Property.objects.get(propertyId=property_id)
        except ObjectDoesNotExist:
            return Response(
                PROPERTY_DOES_NOT_EXIST_RESPONSE, status=status.HTTP_404_NOT_FOUND
            )

        if property.owner != user and property.bidder != user:
            return Response(
                USER_NOT_BIDDER_NOR_OWNER_RESPONSE, status=status.HTTP_403_FORBIDDEN
            )

        try:
            abstract_contract = AbstractContract(
                Contract.objects.get(property=property_id)
            )
        except ObjectDoesNotExist:
            abstract_contract = AbstractContract(None)

        # Hardcoded the private key for the portal
        if (
            abstract_contract.currentStage == ContractStages.SELLER.value
            and property.owner == user
        ):
            seller_contract = SellerContract.objects.create(
                property=property,
                seller=user,
                contractHashIdentifier=generateUserPropertyContractHash(user, property),
                contractAddress=None,
            )
            seller_contract.save()
            contract = Contract.objects.create(
                property=property, sellerContract=seller_contract
            )
            contract.save()
            # Contract hash
            contract_hash = seller_contract.contractHashIdentifier
            signature = signWithPortalPrivateKey(PORTAL_PRIVATE_KEY, contract_hash)
            encrypted_signature = encryptWithUserSha(user.userHash, signature)
            sendMail(
                subject="Details for your property",
                message=f"""Here are your details for the property:
- Property Id: {property.propertyId}
- Property Title: {property.title}
- Contract hash: {contract_hash}
- Encrypted signature: {encrypted_signature}""",
                recipientEmails=[user.email],
            )
            # TODO: Now need to mail both `contract_hash` and `encrypted_signature` to the user

            return Response(
                {"message": "Contract created successfully."},
                status=status.HTTP_201_CREATED,
            )

        if (
            abstract_contract.currentStage == ContractStages.BUYER.value
            and property.bidder == user
        ):
            buyer_contract = BuyerContract.objects.create(
                property=property,
                buyer=user,
                contractHashIdentifier=generateUserPropertyContractHash(user, property),
                contractAddress=None,
            )
            buyer_contract.save()
            contract_hash = buyer_contract.contractHashIdentifier
            signature = signWithPortalPrivateKey(PORTAL_PRIVATE_KEY, contract_hash)
            encrypted_signature = encryptWithUserSha(user.userHash, signature)
            # TODO: Now need to mail both `contract_hash` and `encrypted_signature` to the user

            abstract_contract.contract.buyerContract = buyer_contract
            abstract_contract.contract.save()
            if property.status in ("for_sell", "For Sell"):
                property.status = "Sold"
            elif property.status in ("for_rent", "For Rent"):
                property.status = "Rented"
            property.save()
            return Response(
                {"message": "Contract created successfully."},
                status=status.HTTP_201_CREATED,
            )

        return Response(TRESPASSING_RESPONSE, status=status.HTTP_403_FORBIDDEN)


class ChangeOwnershipView(APIView):
    def post(self, request, property_id):
        if isinstance(request.user, AnonymousUser):
            return Response(USER_SIGNIN_RESPONSE, status=status.HTTP_401_UNAUTHORIZED)

        user = request.user
        try:
            property_obj = Property.objects.get(pk=property_id)
        except ObjectDoesNotExist:
            return Response(
                PROPERTY_DOES_NOT_EXIST_RESPONSE, status=status.HTTP_404_NOT_FOUND
            )

        if property_obj.owner != user:
            return Response(USER_NOT_OWNER_RESPONSE, status=status.HTTP_403_FORBIDDEN)

        # Check proof of identity
        proof_of_identity = (
            request.FILES.get(f"proof_identity_{property_id}")
            if f"proof_identity_{property_id}" in request.FILES
            else None
        )
        if not proof_of_identity or not verifyUserDocument(user, proof_of_identity):
            return Response(
                USER_DOCUMENT_HASH_MISMATCH_RESPONSE, status=status.HTTP_400_BAD_REQUEST
            )

        ownership_document_hash = (
            hashDocument(request.FILES[f"ownership_document_{property_id}"].read())
            if f"ownership_document_{property_id}" in request.FILES
            else None
        )

        if ownership_document_hash is None:
            return Response(
                PROPERTY_OWNERSHIP_DOCUMENT_MISSING_RESPONSE,
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update ownership document if it is not None (it cannot be None because the field is required while adding a property)
        property_obj.ownershipDocumentHash = ownership_document_hash
        property_obj.propertyHashIdentifier = generatePropertyHash(
            ownership_document_hash,
            property_obj.title,
            property_obj.description,
            property_obj.price,
            property_obj.bedrooms,
            property_obj.bathrooms,
            property_obj.area,
            property_obj.status,
            property_obj.location.name,
            property_obj.availabilityDate,
        )
        property_obj.save()
        return Response(
            {"message": "Ownership change successful."},
            status=status.HTTP_200_OK,
        )


class VerifyContractView(APIView):
    def post(self, request):
        try:
            verification_text = request.data.get("verification_string")
            verification_text_bytes = b64decode(verification_text)
            contract_sha_digest = b64decode(request.data.get("contract_sha"))

            # TODO: replace this logic with environment variable
            portal_public_key_bytes = b64decode(PORTAL_PUBLIC_ENCODED_KEY)
            portal_public_key = load_pem_public_key(
                portal_public_key_bytes, backend=default_backend()
            )

            username = request.data.get("user_identifier")
            user = User.objects.get(username=username)
            user_sha = b64decode(user.userHash)

            decrypted_signature = decryptWithUserSha(user_sha, verification_text_bytes)
            verified_contract_sha = verifyWithPortalPublicKey(
                portal_public_key, contract_sha_digest, decrypted_signature
            )

            if verified_contract_sha == contract_sha_digest:
                verification_result = "sanctioned"
            else:
                verification_result = "not_sanctioned"

            print(verification_result)
            context = {"verification_result": verification_result}

        except ObjectDoesNotExist as exception:
            return Response(
                {"error": "User does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as exception:
            print(f"An error occurred: {exception}")
            return Response(
                {"error": "An error occurred during verification."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"verification_result": verification_result},
            status=status.HTTP_200_OK,
        )
