from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .serializers import ChangePasswordSerializer, LoginSerializer, ProfileSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    username = serializer.validated_data.get("username")
    password = serializer.validated_data.get("password")

    user = authenticate(username=username, password=password)

    if user is not None and user.is_staff:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "success": True,
            "message": "Login Successful",
            "token": token.key,
            "profile": ProfileSerializer(user).data,
        })

    return Response({
        "success": False,
        "message": "Invalid username or password"
    }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def profile(request):
    if request.method == "GET":
        return Response(ProfileSerializer(request.user).data)

    serializer = ProfileSerializer(
        request.user,
        data=request.data,
        partial=request.method == "PATCH",
    )
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.save()
    return Response({
        "success": True,
        "message": "Profile updated successfully.",
        "profile": ProfileSerializer(user).data,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(
        data=request.data,
        context={"request": request},
    )
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.save()
    Token.objects.filter(user=user).delete()
    token = Token.objects.create(user=user)

    return Response({
        "success": True,
        "message": "Password changed successfully.",
        "token": token.key,
    })
