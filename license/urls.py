from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LicenseStatusView, LicenseActivationView, VersionActivationView, AccessHistoryViewSet

router = DefaultRouter()
router.register(r'history', AccessHistoryViewSet, basename='license-history')

urlpatterns = [
    path('status/', LicenseStatusView.as_view(), name='license-status'),
    path('activate/', LicenseActivationView.as_view(), name='license-activate'),
    path('version-activate/', VersionActivationView.as_view(), name='version-activate'),
    path('', include(router.urls)),
]
