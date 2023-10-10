from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render
from twentyfiveacres.models import User


def homepage(request):
    """
    @desc: displays homepage ofcourse
    """
    if isinstance(request.user, AnonymousUser):
        context = {"state": "signup"}
        return render(request, "homepage.html", context=context)
    else:
        user = User.objects.get(username=request.user.username)
        context = {"username": user.username, "state": "signin"}
        return render(request, "homepage.html", context=context)
