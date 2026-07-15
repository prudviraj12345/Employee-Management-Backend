from rest_framework import serializers
from .models import EmailLog


class EmailLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmailLog
        fields = "__all__"

        read_only_fields = (
            "status",
            "retry_count",
            "sent_at",
            "created_at",
        )

    def validate(self, data):
        employee = data.get('employee')
        recipient_email = data.get('recipient_email')
        
        if employee and recipient_email:
            if employee.email != recipient_email:
                raise serializers.ValidationError({
                    "recipient_email": f"Recipient email must match the employee's registered email ({employee.email})."
                })
        return data