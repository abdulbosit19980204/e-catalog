from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatSettingsViewSet, ConversationViewSet, ChatMessageViewSet

router = DefaultRouter()
router.register(r'settings', ChatSettingsViewSet)
router.register(r'conversations', ConversationViewSet)
router.register(r'messages', ChatMessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
