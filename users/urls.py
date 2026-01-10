from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OneCLoginView, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('auth/1c-login/', OneCLoginView.as_view(), name='auth-1c-login'),
    path('', include(router.urls)),
]
