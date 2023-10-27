from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render
from twentyfiveacres.models import User

from django.contrib import messages

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # X_FORWARDED_FOR can be a comma-separated list of IPs. The client's requested IP will be the first one.
    else:
        ip = request.META.get('REMOTE_ADDR')  # If not behind a proxy, use this
    return ip

def fake_admin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print("INSIODE")
        ip_address = get_client_ip(request)

        print(f"IP address of user: {ip_address}")
        messages.error(request, f'Warning: Dont try Something funny! Your IP address has been recorded: {ip_address} and proceed to check report')

    return render(request, "admin1.html")
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
