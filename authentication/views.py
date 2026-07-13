from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(["POST"])
def login(request):

    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)

    if user is not None and user.is_staff:
        return Response({
            "success": True,
            "message": "Login Successful"
        })

    return Response({
        "success": False,
        "message": "Invalid username or password"
    }, status=status.HTTP_401_UNAUTHORIZED)