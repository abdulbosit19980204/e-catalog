from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse
from .models import ChatSettings, Conversation, ChatMessage
from .serializers import ChatSettingsSerializer, ConversationSerializer, ChatMessageSerializer

@extend_schema_view(
    list=extend_schema(tags=['Chat'], summary="Chat sozlamalari ro'yxati"),
    retrieve=extend_schema(tags=['Chat'], summary="Bitta chat sozlamasini olish"),
    create=extend_schema(tags=['Chat'], summary="Yangi chat sozlamasi yaratish"),
    update=extend_schema(tags=['Chat'], summary="Chat sozlamasini o'zgartirish"),
    partial_update=extend_schema(tags=['Chat'], summary="Chat sozlamasini qisman o'zgartirish"),
    destroy=extend_schema(tags=['Chat'], summary="Chat sozlamasini o'chirish"),
)
class ChatSettingsViewSet(viewsets.ModelViewSet):
    queryset = ChatSettings.objects.filter(is_deleted=False)
    serializer_class = ChatSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only one active settings object should exist ideally
        return ChatSettings.objects.filter(is_deleted=False)

    @extend_schema(
        tags=['Chat'],
        summary="Hozirgi aktiv chat sozlamalarini olish",
        description="Tizimdagi hozirgi aktiv chat sozlamasini qaytaradi. Agar mavjud bo'lmasa, default yaratadi."
    )
    @action(detail=False, methods=['get'])
    def current(self, request):
        settings = ChatSettings.objects.filter(is_active=True).first()
        if not settings:
            # Create default if not exists
            settings = ChatSettings.objects.create()
        serializer = self.get_serializer(settings)
        return Response(serializer.data)

@extend_schema_view(
    list=extend_schema(
        tags=['Chat'], 
        summary="Suhbatlar (conversations) ro'yxati",
        description="Foydalanuvchiga tegishli (admin bo'lsa barcha) suhbatlar ro'yxatini qaytaradi."
    ),
    retrieve=extend_schema(tags=['Chat'], summary="Suhbat tafsilotlarini olish"),
    create=extend_schema(tags=['Chat'], summary="Yangi suhbat boshlash"),
    update=extend_schema(tags=['Chat'], summary="Suhbat ma'lumotlarini o'zgartirish"),
    partial_update=extend_schema(tags=['Chat'], summary="Suhbatni qisman o'zgartirish"),
    destroy=extend_schema(tags=['Chat'], summary="Suhbatni o'chirish (soft-delete)"),
)
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

    @extend_schema(
        tags=['Chat'],
        summary="Suhbatdagi barcha xabarlarni olish",
        description="Berilgan suhbatga tegishli barcha xabarlarni qaytaradi va boshqa foydalanuvchi yozgan xabarlarni 'o'qildi' (is_read=True) deb belgilaydi.",
        responses={200: ChatMessageSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        conversation = self.get_object()
        messages = conversation.messages.all()
        
        # Mark as read
        messages.exclude(sender=request.user).update(is_read=True)
        
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)

@extend_schema_view(
    list=extend_schema(tags=['Chat'], summary="Barcha xabarlar ro'yxati"),
    retrieve=extend_schema(tags=['Chat'], summary="Xabar tafsiloti"),
    create=extend_schema(
        tags=['Chat'], 
        summary="Xabar yuborish",
        description="Suhbat ichida yangi xabar yuborish. `sender` avtomatik ravishda hozirgi user bo'ladi."
    ),
    update=extend_schema(tags=['Chat'], summary="Xabarni tahrirlash"),
    partial_update=extend_schema(tags=['Chat'], summary="Xabarni qisman tahrirlash"),
    destroy=extend_schema(tags=['Chat'], summary="Xabarni o'chirish"),
)
class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.filter(is_deleted=False)
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
