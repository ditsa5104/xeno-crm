from rest_framework.routers import DefaultRouter
from .views import CampaignTemplateViewSet

router = DefaultRouter()
router.register(r'', CampaignTemplateViewSet, basename='campaign-template')

urlpatterns = router.urls
