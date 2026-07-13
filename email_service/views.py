from rest_framework import viewsets
from django.utils import timezone

from .models import EmailLog
from .serializers import EmailLogSerializer

from history.models import EmailHistory


class EmailLogViewSet(viewsets.ModelViewSet):

    queryset = EmailLog.objects.all()
    serializer_class = EmailLogSerializer

    def perform_create(self, serializer):

        # Save Email
        email = serializer.save()

        # Automatically update status
        email.status = "Sent"
        email.sent_at = timezone.now()
        email.save()

        # Automatically create history
        EmailHistory.objects.create(
            employee=email.employee,
            recipient_email=email.recipient_email,
            subject=email.subject,
            message=email.message,
            status=email.status,
            retry_count=email.retry_count,
            sent_at=email.sent_at
        )