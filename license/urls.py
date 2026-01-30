from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LicenseStatusView, AccessHistoryViewSet

router = DefaultRouter()
router.register(r'history', AccessHistoryViewSet, basename='license-history')

urlpatterns = [
    path('status/', LicenseStatusView.as_view(), name='license-status'),
    path('', include(router.urls)),
]
