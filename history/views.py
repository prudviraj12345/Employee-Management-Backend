from rest_framework import viewsets

from .models import EmailHistory
from .serializers import EmailHistorySerializer


class EmailHistoryViewSet(viewsets.ModelViewSet):

    queryset = EmailHistory.objects.all().order_by("-sent_at")

    serializer_class = EmailHistorySerializer