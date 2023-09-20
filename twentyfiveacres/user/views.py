from django.shortcuts import render
from .models import User


def user_list(request):
    users = User.objects.all()
    print(f"len = {len(users)}")
    return render(request, "user/user_list.html", {"users": users})
