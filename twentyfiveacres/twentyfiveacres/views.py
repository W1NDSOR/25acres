from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render
from twentyfiveacres.models import User
import requests
from user.views import authenticateUser



def homepage(request):
    """
    @desc: displays homepage ofcourse
    """
    if not authenticateUser(request.session['access_token']):
        return render(request, "homepage.html", {"state": "signup"})
    
    else:
        username = request.session['username']
        context = {"username": username, "state": "signin"}
        return render(request, "homepage.html", context=context)