from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HealthViewSet, SystemSettingsViewSet

router = DefaultRouter()
router.register(r'health', HealthViewSet, basename='health')
router.register(r'system-settings', SystemSettingsViewSet, basename='system-settings')

urlpatterns = [
    path('', include(router.urls)),
]
