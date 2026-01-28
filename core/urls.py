from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HealthViewSet, SystemSettingsViewSet, AITokenUsageViewSet, AIModelViewSet

router = DefaultRouter()
router.register(r'health', HealthViewSet, basename='health')
router.register(r'system-settings', SystemSettingsViewSet, basename='system-settings')
router.register(r'ai-usage', AITokenUsageViewSet, basename='ai-usage')
router.register(r'ai-models', AIModelViewSet, basename='ai-models')

urlpatterns = [
    path('', include(router.urls)),
]
