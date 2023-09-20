from django.shortcuts import render
from django.contrib.auth.models import User
from time import time 


def userList(request):
    '''
    Displays the list of users in the database.
    '''

    users = User.objects.all()
    print(f"len = {len(users)}")
    return render(request, "admin/user_list.html", {"users": users})

def addUser(request):
    userFields = request.POST
    username = userFields.get("userName")
    email = userFields.get("email")
    password = userFields.get("password")
    document = userFields.get("document")
    print(userFields)
    if username != None:
        User.objects.create(
            userName=f"debug: {time()}.username",
            email=f"debug{time()}.email@25acres.windsor",
            password="debug: hashed password",
            firstName=f"debug: first name",
            lastName=f"debug: last name",
            phoneNumber=f"debug: (+x) xxx-xxx-xxxx",
            userType="buyer",
            aadharNumber=f"debug: aadhar number",
            documentHash=f"debug: document hash",
        )
    return render(request, "user/add_user_form.html")
