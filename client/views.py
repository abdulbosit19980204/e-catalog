from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample,
)
from drf_spectacular.types import OpenApiTypes
from .models import Client, ClientImage
from .serializers import (
    ClientSerializer,
    ClientImageSerializer,
    ClientImageBulkUploadSerializer,
)


@extend_schema_view(
    list=extend_schema(
        tags=['Clients'],
        summary="Client ro'yxatini olish",
        description=(
            "Authentication talab qilinadi. Client'lar ro'yxatini pagination bilan qaytaradi."
            " `search` parametri orqali `name`, `email` va `client_code_1c` bo'yicha qidirish mumkin."
        ),
        parameters=[
            OpenApiParameter(
                name='search',
                required=False,
                type=OpenApiTypes.STR,
                description="Client nomi, email yoki code bo'yicha qidirish",
            ),
            OpenApiParameter(
                name='page',
                required=False,
                type=OpenApiTypes.INT,
                description="Sahifa raqami (default: 1)",
            ),
            OpenApiParameter(
                name='page_size',
                required=False,
                type=OpenApiTypes.INT,
                description="Sahifadagi elementlar soni (default: 20, max: 100)",
            ),
            OpenApiParameter(
                name='client_code_1c',
                required=False,
                type=OpenApiTypes.STR,
                description="Aniq code bo'yicha filter",
            ),
            OpenApiParameter(
                name='name',
                required=False,
                type=OpenApiTypes.STR,
                description="Aniq nom bo'yicha filter",
            ),
        ],
    ),
    retrieve=extend_schema(
        tags=['Clients'],
        summary="Bitta client ma'lumotini olish",
        description="`client_code_1c` identifikatoriga ko'ra client ma'lumotlarini qaytaradi.",
    ),
    create=extend_schema(
        tags=['Clients'],
        summary="Yangi client yaratish",
        description="Authentication ostida yangi client qo'shish.",
    ),
    update=extend_schema(
        tags=['Clients'],
        summary="Client ma'lumotlarini to'liq yangilash",
        description="`PUT` so'rovi client yozuvini to'liq yangilaydi.",
    ),
    partial_update=extend_schema(
        tags=['Clients'],
        summary="Client ma'lumotlarini qisman yangilash",
        description="Faqat yuborilgan maydonlarni yangilaydi. `client_code_1c` o'zgarmaydi.",
    ),
    destroy=extend_schema(
        tags=['Clients'],
        summary="Client'ni soft-delete qilish",
        description="Client yozuvini `is_deleted=True` qilib belgilaydi.",
        responses={204: OpenApiResponse(description="Client soft-delete qilindi")},
    ),
)
class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.filter(is_deleted=False)
    serializer_class = ClientSerializer
    lookup_field = 'client_code_1c'
    filterset_fields = ['client_code_1c', 'name', 'email']
    search_fields = ['client_code_1c', 'name', 'email']
    permission_classes = [IsAuthenticated]  # Faqat authenticated user'lar uchun
    
    def get_queryset(self):
        """Optimizatsiya: prefetch_related bilan images yuklash - N+1 query muammosini hal qiladi"""
        return Client.objects.filter(
            is_deleted=False
        ).prefetch_related('images').order_by('-created_at')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

@extend_schema_view(
    list=extend_schema(
        tags=['Clients'],
        summary="Client rasmlari ro'yxatini olish",
        description="Client rasmlarini `client` va `is_main` bo'yicha filterlash mumkin.",
        parameters=[
            OpenApiParameter(
                name='client',
                required=False,
                type=OpenApiTypes.STR,
                description="Client code_1c bo'yicha filter",
            ),
            OpenApiParameter(
                name='is_main',
                required=False,
                type=OpenApiTypes.BOOL,
                description="Asosiy rasm bo'yicha filter",
            ),
        ],
    ),
    create=extend_schema(
        tags=['Clients'],
        summary="Client uchun bitta rasm yuklash",
        description="Multipart form-data orqali bitta rasm faylini yuklaydi.",
    ),
    destroy=extend_schema(
        tags=['Clients'],
        summary="Client rasmini o'chirish",
        description="Rasmni bazadan o'chiradi yoki soft-delete qiladi.",
    ),
)
class ClientImageViewSet(viewsets.ModelViewSet):
    queryset = ClientImage.objects.filter(is_deleted=False)
    serializer_class = ClientImageSerializer
    filterset_fields = ['client', 'is_main']
    search_fields = ['client__client_code_1c', 'client__name']
    permission_classes = [IsAuthenticated]  # Faqat authenticated user'lar uchun
    
    def get_queryset(self):
        """Optimizatsiya: select_related bilan client yuklash - N+1 query muammosini hal qiladi"""
        return ClientImage.objects.filter(
            is_deleted=False
        ).select_related('client').order_by('-created_at')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @extend_schema(
        tags=['Clients'],
        summary="Client uchun bir nechta rasm yuklash",
        description=(
            "Multipart form-data formatida bir nechta rasm faylini birdaniga yuklaydi. "
            "`client` maydoniga `client_code_1c` qiymati yuboriladi."
        ),
        request=ClientImageBulkUploadSerializer,
        responses={
            201: OpenApiResponse(
                response=ClientImageSerializer(many=True),
                description="Yangi yuklangan rasmlar ro'yxati",
            ),
            400: OpenApiResponse(description="Kerakli maydonlar yetishmaydi"),
            404: OpenApiResponse(description="Client topilmadi"),
        },
        examples=[
            OpenApiExample(
                name="Multipart sample",
                description="HTTPie yordamida bir nechta client rasmini yuborish",
                value="http --form POST /api/v1/client-images/bulk-upload/ client=C-001 "
                "images@/path/img1.jpg images@/path/img2.jpg",
            )
        ],
    )
    @action(detail=False, methods=['post'], url_path='bulk-upload')
    def bulk_upload(self, request):
        """Bir vaqtda bir nechta rasm yuklash"""
        client_code = request.data.get('client')
        if not client_code:
            return Response(
                {'error': 'client client_code_1c talab qilinadi'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            client = Client.objects.get(client_code_1c=client_code, is_deleted=False)
        except Client.DoesNotExist:
            return Response(
                {'error': 'Client topilmadi'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        images = request.FILES.getlist('images')
        if not images:
            return Response(
                {'error': 'Rasmlar talab qilinadi'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_images = []
        for image in images:
            image_obj = ClientImage.objects.create(
                client=client,
                image=image,
                is_main=False,
                is_active=True,
                is_deleted=False
            )
            serializer = ClientImageSerializer(image_obj, context={'request': request})
            created_images.append(serializer.data)
        
        return Response({
            'message': f'{len(created_images)} ta rasm muvaffaqiyatli yuklandi',
            'images': created_images
        }, status=status.HTTP_201_CREATED)
