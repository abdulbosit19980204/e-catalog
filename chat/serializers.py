from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ChatSettings, Conversation, ChatMessage

User = get_user_model()

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name']

class ChatSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSettings
        fields = '__all__'

class ChatMessageSerializer(serializers.ModelSerializer):
    sender = UserSimpleSerializer(read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'conversation', 'sender', 'body', 'image', 'is_read', 'created_at']
        read_only_fields = ['sender', 'created_at']

class ConversationSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)
    responder = UserSimpleSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'user', 'responder', 'status', 'last_message_at', 'last_message', 'unread_count', 'created_at']

    def get_last_message(self, obj):
        msg = obj.messages.last()
        if msg:
            return ChatMessageSerializer(msg).data
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0
