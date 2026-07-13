from rest_framework import serializers
from .models import EmailHistory


class EmailHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = EmailHistory
        fields = "__all__"

        read_only_fields = (
            "status",
            "retry_count",
            "sent_at",
        )