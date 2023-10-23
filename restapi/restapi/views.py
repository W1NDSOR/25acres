from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from restapi.models import User

class GetUserByUsername(APIView):
    def get(self, request):
        try:
            user = User.objects.get(username=request.user.username)

            data = {"username": user.username, "state": "signin"}
            return Response(data, status=True)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=False)
