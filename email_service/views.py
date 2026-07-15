import logging
from rest_framework import viewsets
from django.utils import timezone
from django.core.mail import EmailMessage

from .models import EmailLog, EmailTemplate
from .serializers import EmailLogSerializer, EmailTemplateSerializer
from history.models import EmailHistory

logger = logging.getLogger(__name__)


def send_email_async(email_id, email_message):
    import logging
    from django.utils import timezone
    from django.db import connections
    from email_service.models import EmailLog
    from history.models import EmailHistory

    logger = logging.getLogger(__name__)

    try:
        email_message.send(fail_silently=False)
        status = "Sent"
    except Exception as e:
        logger.exception(f"Failed to send email in background: {str(e)}")
        status = "Failed"

    try:
        email = EmailLog.objects.get(id=email_id)
        email.status = status
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
    except Exception as db_err:
        logger.exception(f"Database error updating email log: {str(db_err)}")
    finally:
        connections.close_all()


class EmailLogViewSet(viewsets.ModelViewSet):

    queryset = EmailLog.objects.all()
    serializer_class = EmailLogSerializer

    def perform_create(self, serializer):
        import threading

        # Save Email initially as Sending
        email = serializer.save()
        email.status = 'Sending'
        email.save()

        # Create EmailMessage instance to support attachments
        email_message = EmailMessage(
            subject=email.subject,
            body=email.message,
            from_email=None,  # Defaults to DEFAULT_FROM_EMAIL in settings
            to=[email.recipient_email],
        )
        
        # Retrieve attachment from request FILES if uploaded
        attachment_file = self.request.FILES.get('attachment') or self.request.data.get('attachment')
        if attachment_file:
            import os
            attachment_file.seek(0)
            content = attachment_file.read()
            attachment_file.seek(0)  # Reset pointer

            filename = attachment_file.name
            content_type = attachment_file.content_type

            # Check magic bytes for PDF to force application/pdf
            if content.startswith(b'%PDF-'):
                content_type = 'application/pdf'
                if not filename.lower().endswith('.pdf'):
                    filename = f"{os.path.splitext(filename)[0]}.pdf"
            else:
                # Dynamically guess the mimetype based on the filename/extension
                import mimetypes
                guessed_type, _ = mimetypes.guess_type(filename)
                if guessed_type:
                    content_type = guessed_type
                elif attachment_file.content_type:
                    # Fallback to browser-passed content-type
                    content_type = attachment_file.content_type
                else:
                    # Standard fallback for arbitrary binary files
                    content_type = 'application/octet-stream'

            email_message.attach(
                filename,
                content,
                content_type
            )

        # Spawn background sending thread
        t = threading.Thread(target=send_email_async, args=(email.id, email_message))
        t.start()


class EmailTemplateViewSet(viewsets.ModelViewSet):
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer