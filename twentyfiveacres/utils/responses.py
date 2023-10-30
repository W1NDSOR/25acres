from django.http import JsonResponse

USER_SIGNIN_RESPONSE = JsonResponse(
    {"result": "Identity crisis", "message": "Sign in first"}
)

USER_DOCUMENT_HASH_MISMATCH_RESPONSE = JsonResponse(
    {
        "result": "Identity Crisis",
        "message": "Record for existencial proof missing",
    }
)

CANNOT_BID_TO_OWN_PROPERTY_RESPONSE = JsonResponse(
    {"result": "Identity crisis", "message": "Cannot bid to your own property lmao"}
)

PROPERTY_DOES_NOT_EXIST_RESPONSE = JsonResponse(
    {"result": "Existential crisis", "message": "Mentioned property does not exist"}
)

PROPERTY_OWNERSHIP_DOCUMENT_MISSING_RESPONSE = JsonResponse(
    {"result": "Existential crisis", "message": "Missing property ownership document"}
)

BIDDING_CLOSED_RESPONSE = JsonResponse(
    {
        "result": "Time drift exception",
        "message": "Bid already closed",
    }
)

USER_EMAIL_ROLLNUMBER_MISMATCH_RESPONSE = JsonResponse(
    {
        "result": "Value Mismatch Exception",
        "message": "Roll number and email does not match",
    }
)

USER_INVALID_EMAIL_FORMAT_RESPONSE = JsonResponse(
    {
        "result": "Value Mismatch Exception",
        "message": "Email is not in valid IIITD format",
    }
)

USER_INVALID_CODE_OR_ROLLNUMBER_RESPONSE = JsonResponse(
    {
        "result": "Identity crisis",
        "message": "Invalid verification code or rollnumber",
    }
)

USER_INVALID_ROLLNUMBER_RESPONSE = JsonResponse(
    {
        "result": "Identity crisis",
        "message": "User with provided roll number does not exists",
    }
)

USER_INVALID_PASSWORD_RESPONSE = JsonResponse(
    {
        "result": "Identity crisis",
        "message": "Invalid password",
    }
)


USER_NOT_OWNER_RESPONSE = JsonResponse(
    {
        "result": "Identity crisis",
        "message": "Thou art not the owner of this property",
    }
)

USER_NOT_BIDDER_NOR_OWNER_RESPONSE = JsonResponse(
    {
        "result": "Identity crisis",
        "message": "Thou art not bidder nor the owner of this property",
    }
)

TRESPASSING_RESPONSE = JsonResponse(
    {"result": "Trespassing", "message": "Wandering into unbeknownst valleys"}
)


USER_SIGNIN_WITHOUT_VERIFICATION_REPONSE = JsonResponse(
    {
        "result": "Caught commiting treason",
        "message": "Thou caught trying to signin before email verification",
    }
)
