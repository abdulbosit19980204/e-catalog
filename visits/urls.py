from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VisitViewSet, VisitPlanViewSet, VisitImageViewSet

router = DefaultRouter()
router.register('visit', VisitViewSet, basename='visit')
router.register('visit-plan', VisitPlanViewSet, basename='visit-plan')
router.register('visit-image', VisitImageViewSet, basename='visit-image')

urlpatterns = router.urls
