import os
import logging
import mimetypes
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.core.mail import EmailMessage
from django.core import mail

from .models import EmailLog, EmailTemplate
from .serializers import EmailLogSerializer, EmailTemplateSerializer
from history.models import EmailHistory

logger = logging.getLogger(__name__)


def _build_email_message(subject, body, to_email, connection=None, attachment_content=None, attachment_name=None, attachment_content_type=None):
    """Helper to construct an EmailMessage with optional attachment."""
    msg = EmailMessage(
        subject=subject,
        body=body,
        from_email=None,  # Falls back to DEFAULT_FROM_EMAIL in settings
        to=[to_email],
        connection=connection,
    )
    if attachment_content and attachment_name:
        msg.attach(attachment_name, attachment_content, attachment_content_type or 'application/octet-stream')
    return msg


def _resolve_attachment(file_obj):
    """Read attachment content and detect its MIME type. Returns (content, name, content_type)."""
    if not file_obj:
        return None, None, None

    file_obj.seek(0)
    content = file_obj.read()
    file_obj.seek(0)

    name = file_obj.name
    content_type = file_obj.content_type

    if content.startswith(b'%PDF-'):
        content_type = 'application/pdf'
        if not name.lower().endswith('.pdf'):
            name = os.path.splitext(name)[0] + '.pdf'
    else:
        guessed, _ = mimetypes.guess_type(name)
        if guessed:
            content_type = guessed
        elif not content_type:
            content_type = 'application/octet-stream'

    return content, name, content_type


def _save_history(email_log):
    """Persist an EmailHistory record from an EmailLog object."""
    EmailHistory.objects.create(
        employee=email_log.employee,
        recipient_email=email_log.recipient_email,
        subject=email_log.subject,
        message=email_log.message,
        status=email_log.status,
        retry_count=email_log.retry_count,
        sent_at=email_log.sent_at,
    )


class EmailLogViewSet(viewsets.ModelViewSet):

    queryset = EmailLog.objects.all()
    serializer_class = EmailLogSerializer

    def perform_create(self, serializer):
        """Handle single email dispatch (one recipient at a time)."""
        email = serializer.save()
        email.status = 'Sending'
        email.save()

        # Resolve attachment once
        attachment_file = self.request.FILES.get('attachment') or self.request.data.get('attachment')
        att_content, att_name, att_content_type = _resolve_attachment(attachment_file)

        email_message = _build_email_message(
            subject=email.subject,
            body=email.message,
            to_email=email.recipient_email,
            attachment_content=att_content,
            attachment_name=att_name,
            attachment_content_type=att_content_type,
        )

        try:
            email_message.send(fail_silently=False)
            email.status = 'Sent'
        except Exception as e:
            logger.exception(f"Failed to send email to {email.recipient_email}: {e}")
            email.status = 'Failed'

        email.sent_at = timezone.now()
        email.save()
        _save_history(email)

    @action(detail=False, methods=['post'])
    def batch_send(self, request):
        """
        Efficient batch email dispatch using a single persistent SMTP connection.
        Expects: employees[] (list of IDs), subject, message, optional attachment.
        Returns: { success_count, total_count }
        """
        from employee.models import Employee

        employee_ids = request.data.getlist('employees')
        subject_tpl = request.data.get('subject', '')
        message_tpl = request.data.get('message', '')

        if not employee_ids:
            return Response({'error': 'No employees selected.'}, status=status.HTTP_400_BAD_REQUEST)

        # Resolve attachment once (avoids repeated stream reads)
        attachment_file = request.FILES.get('attachment') or request.data.get('attachment')
        att_content, att_name, att_content_type = _resolve_attachment(attachment_file)

        success_count = 0
        total_count = len(employee_ids)

        # Open one SMTP connection for the entire batch
        connection = mail.get_connection()
        try:
            connection.open()
        except Exception as e:
            logger.exception(f"Could not open SMTP connection: {e}")
            return Response({'error': 'SMTP connection failed. Check email settings.'}, status=status.HTTP_502_BAD_GATEWAY)

        for emp_id in employee_ids:
            try:
                emp = Employee.objects.get(id=emp_id)
            except Employee.DoesNotExist:
                logger.warning(f"Employee with id={emp_id} not found, skipping.")
                continue

            rendered_subject = (subject_tpl
                                .replace('{{first_name}}', emp.first_name or '')
                                .replace('{{last_name}}', emp.last_name or '')
                                .replace('{{employee_id}}', emp.employee_id or ''))

            rendered_message = (message_tpl
                                .replace('{{first_name}}', emp.first_name or '')
                                .replace('{{last_name}}', emp.last_name or '')
                                .replace('{{employee_id}}', emp.employee_id or ''))

            email_log = EmailLog.objects.create(
                employee=emp,
                recipient_email=emp.email,
                subject=rendered_subject,
                message=rendered_message,
                status='Sending',
            )

            email_message = _build_email_message(
                subject=rendered_subject,
                body=rendered_message,
                to_email=emp.email,
                connection=connection,
                attachment_content=att_content,
                attachment_name=att_name,
                attachment_content_type=att_content_type,
            )

            try:
                email_message.send(fail_silently=False)
                email_log.status = 'Sent'
                success_count += 1
            except Exception as e:
                logger.exception(f"Failed to send email to {emp.email}: {e}")
                email_log.status = 'Failed'

            email_log.sent_at = timezone.now()
            email_log.save()
            _save_history(email_log)

        try:
            connection.close()
        except Exception:
            pass

        return Response({
            'success_count': success_count,
            'total_count': total_count,
        })


class EmailTemplateViewSet(viewsets.ModelViewSet):
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer