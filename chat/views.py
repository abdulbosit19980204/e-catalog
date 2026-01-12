from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse
from .models import ChatSettings, Conversation, ChatMessage
from .serializers import ChatSettingsSerializer, ConversationSerializer, ChatMessageSerializer

@extend_schema_view(
    list=extend_schema(
        tags=['Chat'], 
        summary="Chat sozlamalari ro'yxati",
        description="Tizimdagi barcha chat sozlamalarini ko'rish."
    ),
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
        description="""
Foydalanuvchiga tegishli (admin bo'lsa barcha) suhbatlar ro'yxatini qaytaradi.

### 1C Foydalanuvchilari uchun Chat tizimi:
1C orqali autentifikatsiya qilingan foydalanuvchilar (masalan: `ТП-3`) chatdan to'liq foydalanishlari mumkin.

### Chat bilan ishlash tartibi:
1. **Suhbatni boshlash**: POST `/conversations/` - Yangi suhbat (conversation) yaratadi. 
   - *Eslatma*: Agar suhbat allaqachon mavjud bo'lsa, u existing suhbatni qaytaradi.
2. **WebSocket ulanishi**: 
   - **URL**: `ws://HOST/ws/chat/{conversation_id}/?token=YOUR_ACCESS_TOKEN`
   - **Autentifikatsiya**: `token` parametri orqali 1C dan olingan `access` tokenini yuboring.
3. **Xabar yuborish (Matn)**: WebSocket orqali JSON yuboring:
   ```json
   {
     "type": "message",
     "body": "Xabar matni"
   }
   ```
4. **Xabar yuborish (Fayl/Skrinshot)**: POST `/messages/` orqali `multipart/form-data` yuboring.
   - Maydonlar: `conversation`, `body` (ixtiyoriy), `file` (skrinshot yoki fayl).
   - *Real-time*: Fayl yuborilganda backend WebSocket orqali barchaga bildirishnoma yuboradi.

### Developer Setup (Serverda ishga tushirish):
WebSocketlar ishlashi uchun serverda quyidagilar ishga tushirilgan bo'lishi shart:
- **Redis Server**: **Redis 5.0+** talab qilinadi (`BZPOPMIN` buyrug'i uchun). 
  - *Windows uchun*: Memurai yoki WSL dagi Redis dan foydalanish tavsiya etiladi. Standart MSOpenTech Redis (3.0.x) ishlata olmaydi.
- **ASGI Server**: `daphne -p 8000 config.asgi:application` (Developmentda `python manage.py runserver` ham ASGI ni qo'llab-quvvatlaydi).
- **Python**: Tizim Python 3.14+ ni qo'llab-quvvatlaydi (Daphne 4.2.1+ va Channels 4.3.2+ orqali).
        """
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
        instance = serializer.save(sender=self.request.user)
        
        # Broadcast to WebSocket group
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{instance.conversation.id}',
            {
                'type': 'chat_message',
                'message': ChatMessageSerializer(instance).data
            }
        )
