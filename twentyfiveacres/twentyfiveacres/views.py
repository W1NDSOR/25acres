from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render
from twentyfiveacres.models import User


def homepage(request):
    """
    @desc: displays homepage ofcourse
    """
    if isinstance(request.user, AnonymousUser):
        return render(request, "homepage_signup.html")
    else:
        user = User.objects.get(username=request.user.username)
        context = {"username": user.username}
        return render(request, "homepage_signout.html", context=context)
