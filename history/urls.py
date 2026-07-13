from rest_framework.routers import DefaultRouter
from .views import EmailHistoryViewSet

router = DefaultRouter()

router.register(r'history', EmailHistoryViewSet)

urlpatterns = router.urls