import logging
from rest_framework import viewsets
from django.utils import timezone
from django.core.mail import EmailMessage

from .models import EmailLog, EmailTemplate
from .serializers import EmailLogSerializer, EmailTemplateSerializer
from history.models import EmailHistory

logger = logging.getLogger(__name__)


class EmailLogViewSet(viewsets.ModelViewSet):

    queryset = EmailLog.objects.all()
    serializer_class = EmailLogSerializer

    def perform_create(self, serializer):
        # Save Email
        email = serializer.save()

        try:
            # Create EmailMessage instance to support attachments
            email_message = EmailMessage(
                subject=email.subject,
                body=email.message,
                from_email=None,  # Defaults to DEFAULT_FROM_EMAIL in settings
                to=[email.recipient_email],
            )
            
            # Retrieve attachment from request FILES if uploaded
            attachment_file = self.request.FILES.get('attachment')
            if attachment_file:
                email_message.attach(
                    attachment_file.name,
                    attachment_file.read(),
                    attachment_file.content_type
                )

            email_message.send(fail_silently=False)
            email.status = "Sent"
        except Exception as e:
            logger.exception(f"Failed to send email to {email.recipient_email}: {str(e)}")
            email.status = "Failed"

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


class EmailTemplateViewSet(viewsets.ModelViewSet):
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer