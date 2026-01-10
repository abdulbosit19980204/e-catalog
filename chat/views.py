from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import ChatSettings, Conversation, ChatMessage
from .serializers import ChatSettingsSerializer, ConversationSerializer, ChatMessageSerializer

class ChatSettingsViewSet(viewsets.ModelViewSet):
    queryset = ChatSettings.objects.filter(is_deleted=False)
    serializer_class = ChatSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only one active settings object should exist ideally
        return ChatSettings.objects.filter(is_deleted=False)

    @action(detail=False, methods=['get'])
    def current(self, request):
        settings = ChatSettings.objects.filter(is_active=True).first()
        if not settings:
            # Create default if not exists
            settings = ChatSettings.objects.create()
        serializer = self.get_serializer(settings)
        return Response(serializer.data)

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.filter(is_deleted=False)
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Conversation.objects.filter(is_deleted=False)
        return Conversation.objects.filter(user=user, is_deleted=False)

    def perform_create(self, serializer):
        # Current user is the owner
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        conversation = self.get_object()
        messages = conversation.messages.all()
        
        # Mark as read
        messages.exclude(sender=request.user).update(is_read=True)
        
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)

class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.filter(is_deleted=False)
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
