from rest_framework.routers import DefaultRouter
from .views import EmailLogViewSet

router = DefaultRouter()
router.register(r'emails', EmailLogViewSet, basename='emails')

urlpatterns = router.urls