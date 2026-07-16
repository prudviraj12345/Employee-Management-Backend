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


def _send_batch_thread(log_ids, att_content, att_name, att_content_type):
    """
    Background thread: sends emails for already-created EmailLog records.
    Receives only primitive data (IDs + bytes) so no ORM objects cross thread boundary.
    """
    from django.db import close_old_connections
    from django.utils import timezone
    from django.core import mail
    from email_service.models import EmailLog
    from history.models import EmailHistory

    # Give Django fresh DB connections inside the thread
    close_old_connections()

    connection = mail.get_connection()
    try:
        connection.open()
    except Exception as e:
        logger.exception(f"[batch_thread] SMTP connection failed: {e}")
        # Mark all as Failed
        for log_id in log_ids:
            try:
                log = EmailLog.objects.get(id=log_id)
                log.status = 'Failed'
                log.sent_at = timezone.now()
                log.save()
                EmailHistory.objects.create(
                    employee=log.employee,
                    recipient_email=log.recipient_email,
                    subject=log.subject,
                    message=log.message,
                    status='Failed',
                    retry_count=log.retry_count,
                    sent_at=log.sent_at,
                )
            except Exception:
                pass
        close_old_connections()
        return

    for log_id in log_ids:
        try:
            log = EmailLog.objects.get(id=log_id)
        except Exception:
            continue

        email_message = _build_email_message(
            subject=log.subject,
            body=log.message,
            to_email=log.recipient_email,
            connection=connection,
            attachment_content=att_content,
            attachment_name=att_name,
            attachment_content_type=att_content_type,
        )

        try:
            email_message.send(fail_silently=False)
            log.status = 'Sent'
        except Exception as e:
            logger.exception(f"[batch_thread] Failed to send to {log.recipient_email}: {e}")
            log.status = 'Failed'

        log.sent_at = timezone.now()
        log.save()

        try:
            EmailHistory.objects.create(
                employee=log.employee,
                recipient_email=log.recipient_email,
                subject=log.subject,
                message=log.message,
                status=log.status,
                retry_count=log.retry_count,
                sent_at=log.sent_at,
            )
        except Exception as e:
            logger.exception(f"[batch_thread] History write failed for {log.recipient_email}: {e}")

    try:
        connection.close()
    except Exception:
        pass

    close_old_connections()


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
        Queues a batch of emails and returns 202 immediately.
        Sending happens in a background thread — no Gunicorn timeout risk.
        Expects: employees[] (list of IDs), subject, message, optional attachment.
        Returns: { queued: N }
        """
        import threading
        from employee.models import Employee

        employee_ids = request.data.getlist('employees')
        subject_tpl = request.data.get('subject', '')
        message_tpl = request.data.get('message', '')

        if not employee_ids:
            return Response({'error': 'No employees selected.'}, status=status.HTTP_400_BAD_REQUEST)

        # Read attachment BEFORE returning — request object won't exist in the thread
        attachment_file = request.FILES.get('attachment') or request.data.get('attachment')
        att_content, att_name, att_content_type = _resolve_attachment(attachment_file)

        # Create all EmailLog records synchronously (committed to DB before thread starts)
        log_ids = []
        for emp_id in employee_ids:
            try:
                emp = Employee.objects.get(id=emp_id)
            except Employee.DoesNotExist:
                logger.warning(f"Employee id={emp_id} not found, skipping.")
                continue

            rendered_subject = (subject_tpl
                                .replace('{{first_name}}', emp.first_name or '')
                                .replace('{{last_name}}', emp.last_name or '')
                                .replace('{{employee_id}}', emp.employee_id or ''))

            rendered_message = (message_tpl
                                .replace('{{first_name}}', emp.first_name or '')
                                .replace('{{last_name}}', emp.last_name or '')
                                .replace('{{employee_id}}', emp.employee_id or ''))

            log = EmailLog.objects.create(
                employee=emp,
                recipient_email=emp.email,
                subject=rendered_subject,
                message=rendered_message,
                status='Queued',
            )
            log_ids.append(log.id)

        if not log_ids:
            return Response({'error': 'No valid employees found.'}, status=status.HTTP_400_BAD_REQUEST)

        # Spawn background thread — all DB records are committed, safe to read by ID
        t = threading.Thread(
            target=_send_batch_thread,
            args=(log_ids, att_content, att_name, att_content_type),
            daemon=True
        )
        t.start()

        # Return immediately — frontend doesn't wait for SMTP
        return Response({'queued': len(log_ids)}, status=status.HTTP_202_ACCEPTED)


class EmailTemplateViewSet(viewsets.ModelViewSet):
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer