from django.shortcuts import render
from twentyfiveacres.models import User
from utils.hashing import hashDocument


def userList(request):
    """
    @desc: displays the list of users in the database.
    """

    users = User.objects.all()
    print(f"len = {len(users)}")
    return render(request, "admin/user_list.html", {"users": users})


def addUser(request):
    """
    @desc: renders a form for adding new user
    """
    userFields = request.POST
    username = userFields.get("user_name")
    email = userFields.get("email")
    password = userFields.get("password")
    firstName = userFields.get("first_name")
    lastName = userFields.get("last_name")
    phoneNumber = userFields.get("phone_number")
    userType = userFields.get("user_type")
    aadharNumber = userFields.get("aadhar_number")
    if "document" in request.FILES:
        document = request.FILES["document"].read()
        documentHash = hashDocument(document)
    else:
        documentHash = None
    # just a precaution, as all the fields are required
    if (
        username
        and email
        and password
        and firstName
        and lastName
        and phoneNumber
        and userType
        and aadharNumber
        and documentHash
    ):
        User.objects.create(
            userName=username,
            email=email,
            password=password,
            firstName=firstName,
            lastName=lastName,
            phoneNumber=phoneNumber,
            userType=userType,
            aadharNumber=aadharNumber,
            documentHash=documentHash,
        )
    return render(request, "user/add_user_form.html")
