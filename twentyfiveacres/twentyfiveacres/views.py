from django.shortcuts import render
from twentyfiveacres.models import User
from django.contrib.auth.models import AnonymousUser


def homepage(request):
    """
    @desc: displays homepage ofcourse
    """
    if isinstance(request.user, AnonymousUser):
        return render(request, "homepage_signup.html")
    else:
        user = User.objects.get(username=request.user.username)
        print(f"rollnumber: {user.rollNumber}")
        context = {"username": user.username, "user_type": user.userType}
        return render(request, "homepage_signout.html", context=context)
