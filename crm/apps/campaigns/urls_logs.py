from rest_framework.routers import DefaultRouter
from .views import CommunicationLogViewSet

router = DefaultRouter()
router.register(r'', CommunicationLogViewSet, basename='communication-log')

urlpatterns = router.urls
