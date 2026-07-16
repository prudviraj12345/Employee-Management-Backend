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


@api_view(["GET"])
@permission_classes([AllowAny])
def public_stats(request):
    from employee.models import Employee
    from email_service.models import EmailLog
    from django.utils import timezone

    # Total synced employees
    total_employees = Employee.objects.count()
    
    # Emails sent today (local time / server time)
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    sent_today = EmailLog.objects.filter(sent_at__gte=today_start, status='Sent').count()
    
    # Delivery rate: (Sent emails / Total emails) * 100
    total_emails = EmailLog.objects.count()
    if total_emails > 0:
        sent_emails = EmailLog.objects.filter(status='Sent').count()
        delivery_rate = f"{int((sent_emails / total_emails) * 100)}%"
    else:
        delivery_rate = "100%"
        
    return Response({
        "employees_synced": total_employees,
        "sent_today": sent_today,
        "delivery_rate": delivery_rate
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def email_check(request):
    """
    Diagnostic endpoint: checks email backend config and tests SMTP connection.
    Hit /api/email-check/ on Render to diagnose email issues.
    """
    from django.conf import settings
    from django.core import mail

    config = {
        "EMAIL_BACKEND": settings.EMAIL_BACKEND,
        "EMAIL_HOST": settings.EMAIL_HOST,
        "EMAIL_PORT": settings.EMAIL_PORT,
        "EMAIL_USE_TLS": settings.EMAIL_USE_TLS,
        "EMAIL_HOST_USER": settings.EMAIL_HOST_USER or "(NOT SET)",
        "EMAIL_HOST_PASSWORD": "SET" if settings.EMAIL_HOST_PASSWORD else "(NOT SET)",
        "DEFAULT_FROM_EMAIL": settings.DEFAULT_FROM_EMAIL,
    }

    if 'smtp' not in settings.EMAIL_BACKEND.lower():
        return Response({
            "status": "misconfigured",
            "message": "Using console backend — emails are printed to logs, NOT sent. Set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD environment variables in Render.",
            "config": config
        }, status=500)

    # Try opening an SMTP connection
    connection = mail.get_connection()
    try:
        connection.open()
        connection.close()
        smtp_ok = True
        smtp_error = None
    except Exception as e:
        smtp_ok = False
        smtp_error = str(e)

    return Response({
        "status": "ok" if smtp_ok else "smtp_error",
        "smtp_connection": "success" if smtp_ok else f"FAILED: {smtp_error}",
        "config": config
    }, status=200 if smtp_ok else 503)

