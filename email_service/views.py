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
        with open('debug_upload.txt', 'a') as f:
            f.write(f"\n--- Request received ---\n")
            f.write(f"FILES: {list(self.request.FILES.keys())}\n")
            f.write(f"FILES details: {self.request.FILES}\n")
            f.write(f"DATA keys: {list(self.request.data.keys())}\n")
            
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

                with open('debug_upload.txt', 'a') as f:
                    f.write(f"Attaching file: {filename}, size: {attachment_file.size}, content_type: {content_type}\n")

                email_message.attach(
                    filename,
                    content,
                    content_type
                )
            else:
                with open('debug_upload.txt', 'a') as f:
                    f.write("No attachment found in FILES or data.\n")

            email_message.send(fail_silently=False)
            with open('debug_upload.txt', 'a') as f:
                f.write("Email sent successfully!\n")
            email.status = "Sent"
        except Exception as e:
            with open('debug_upload.txt', 'a') as f:
                f.write(f"Failed to send email to {email.recipient_email}: {str(e)}\n")
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