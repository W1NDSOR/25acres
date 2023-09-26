from django.shortcuts import render
from twentyfiveacres.models import User
from utils.hashing import hashDocument
from django.http import HttpResponseRedirect
from django.contrib.auth.hashers import make_password
from django.contrib.auth import login
from django.contrib.auth.models import AnonymousUser


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
            return HttpResponseRedirect("../signin")
    return render(request, "user/signup_form.html")


def signin(request):
    """
    @desc: renders a form for signing up new user
    """
    if request.method == "POST":
        userFields = request.POST
        rollNumber = userFields.get("roll_number")
        password = userFields.get("password")
        # just a precaution, as all the fields are required
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
    context = {
        "username": user.username,
        "roll_number": user.rollNumber,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "user_type": user.userType,
    }
    if request.method == "POST":
        userFields = request.POST
        firstName = userFields.get("first_name")
        lastName = userFields.get("last_name")
        # just a precaution, as all the fields are required
        if firstName and lastName:
            user.first_name = firstName
            user.last_name = lastName
            user.save()
            return HttpResponseRedirect("/")
    return render(request, "user/profile.html", context=context)
