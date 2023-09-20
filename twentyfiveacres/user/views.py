from django.shortcuts import render
from .models import User
from time import time
from utils.hasher import hashImage
from os import getcwd
from os.path import join, isfile


def user_list(request):
    users = User.objects.all()
    print(f"len = {len(users)}")
    return render(request, "user/user_list.html", {"users": users})


def addUser(request):
    userFields = request.POST
    username = userFields.get("user_name")
    email = userFields.get("email")
    password = userFields.get("password")
    documentPath = userFields.get("document")
    documentPath = join(getcwd(), documentPath)
    print(isfile(documentPath))
    print(documentPath)
    documentHash = hashImage(documentPath)
    print(documentHash)
    print(userFields)
    if username != None:
        User.objects.create(
            username=f"debug: {time()}.username",
            email=f"debug{time()}.email@25acres.windsor",
            password="debug: hashed password",
            first_name=f"debug: first name",
            last_name=f"debug: last name",
            phone_number=f"debug: (+x) xxx-xxx-xxxx",
            user_type="buyer",
            aadhar_number=f"debug: aadhar number",
            document_hash=f"debug: document hash",
        )
    return render(request, "add_user_form.html")
