from django.db import models
from employee.models import Employee


class EmailLog(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Sending', 'Sending'),
        ('Sent', 'Sent'),
        ('Failed', 'Failed'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='emails'
    )

    recipient_email = models.EmailField()

    subject = models.CharField(max_length=255)

    message = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    retry_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.subject