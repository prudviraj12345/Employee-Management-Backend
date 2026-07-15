from rest_framework.routers import DefaultRouter
from .views import EmailLogViewSet, EmailTemplateViewSet

router = DefaultRouter()
router.register(r'emails', EmailLogViewSet, basename='emails')
router.register(r'templates', EmailTemplateViewSet, basename='templates')

urlpatterns = router.urls