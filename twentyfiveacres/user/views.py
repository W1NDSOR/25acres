from django.shortcuts import render
from twentyfiveacres.models import User
from utils.hashing import hashDocument
from django.http import HttpResponseRedirect
from django.contrib.auth.hashers import make_password


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
    rollNumber = userFields.get("roll_number")
    email = userFields.get("email")
    password = userFields.get("password")
    firstName = userFields.get("first_name")
    lastName = userFields.get("last_name")
    userType = userFields.get("user_type")
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
        and rollNumber
        and userType
        and documentHash
    ):
        user = User.objects.create(
            username=username,
            email=email,
            rollNumber=rollNumber,
            password=make_password(password),
            first_name=firstName,
            last_name=lastName,
            userType=userType,
            documentHash=documentHash,
        )
        user.save()
        return HttpResponseRedirect("/")
    return render(request, "user/add_user_form.html")
