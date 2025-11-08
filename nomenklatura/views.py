from nomenklatura.models import Nomenklatura, NomenklaturaImage
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample,
)
from drf_spectacular.types import OpenApiTypes
from .serializers import (
    NomenklaturaSerializer,
    NomenklaturaImageSerializer,
    NomenklaturaImageBulkUploadSerializer,
)


@extend_schema_view(
    list=extend_schema(
        tags=['Nomenklatura'],
        summary="Nomenklatura ro'yxatini olish",
        description=(
            "Aktiv va soft-delete qilinmagan nomenklaturalarning ro'yxatini qaytaradi."
            " `search` parametri `code_1c` va `name` bo'yicha qidirish imkonini beradi."
        ),
        parameters=[
            OpenApiParameter(
                name='search',
                required=False,
                type=OpenApiTypes.STR,
                description="Nomenklatura nomi yoki code bo'yicha qidirish",
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
                name='code_1c',
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
        tags=['Nomenklatura'],
        summary="Bitta nomenklatura ma'lumotini olish",
        description="`code_1c` identifikatoriga ko'ra nomenklatura ma'lumotlarini qaytaradi.",
    ),
    create=extend_schema(
        tags=['Nomenklatura'],
        summary="Yangi nomenklatura yaratish",
        description="Yangi nomenklatura yozuvini yaratadi.",
    ),
    update=extend_schema(
        tags=['Nomenklatura'],
        summary="Nomenklatura ma'lumotlarini to'liq yangilash",
        description="`PUT` so'rovi nomenklatura yozuvini to'liq yangilaydi.",
    ),
    partial_update=extend_schema(
        tags=['Nomenklatura'],
        summary="Nomenklatura ma'lumotlarini qisman yangilash",
        description="Faqat yuborilgan maydonlarni yangilaydi. `code_1c` o'zgarmaydi.",
    ),
    destroy=extend_schema(
        tags=['Nomenklatura'],
        summary="Nomenklaturani soft-delete qilish",
        description="Nomenklatura yozuvini `is_deleted=True` qilib belgilaydi.",
        responses={204: OpenApiResponse(description="Nomenklatura soft-delete qilindi")},
    ),
)
class NomenklaturaViewSet(viewsets.ModelViewSet):
    queryset = Nomenklatura.objects.filter(is_deleted=False)
    serializer_class = NomenklaturaSerializer
    lookup_field = 'code_1c'
    filterset_fields = ['code_1c', 'name']
    search_fields = ['code_1c', 'name']
    
    def get_queryset(self):
        """Optimizatsiya: prefetch_related bilan images yuklash - N+1 query muammosini hal qiladi"""
        return Nomenklatura.objects.filter(
            is_deleted=False
        ).prefetch_related('images').order_by('-created_at')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

@extend_schema_view(
    list=extend_schema(
        tags=['Nomenklatura'],
        summary="Nomenklatura rasmlari ro'yxatini olish",
        description="Rasmlarni `nomenklatura` va `is_main` bo'yicha filterlash mumkin.",
        parameters=[
            OpenApiParameter(
                name='nomenklatura',
                required=False,
                type=OpenApiTypes.STR,
                description="Nomenklatura code_1c bo'yicha filter",
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
        tags=['Nomenklatura'],
        summary="Nomenklatura uchun bitta rasm yuklash",
        description="Multipart form-data orqali bitta rasm faylini yuklaydi.",
    ),
    destroy=extend_schema(
        tags=['Nomenklatura'],
        summary="Nomenklatura rasmini o'chirish",
        description="Rasmni bazadan o'chiradi yoki soft-delete qiladi.",
    ),
)
class NomenklaturaImageViewSet(viewsets.ModelViewSet):
    queryset = NomenklaturaImage.objects.filter(is_deleted=False)
    serializer_class = NomenklaturaImageSerializer
    filterset_fields = ['nomenklatura', 'is_main']
    search_fields = ['nomenklatura__code_1c', 'nomenklatura__name']
    
    def get_queryset(self):
        """Optimizatsiya: select_related bilan nomenklatura yuklash - N+1 query muammosini hal qiladi"""
        return NomenklaturaImage.objects.filter(
            is_deleted=False
        ).select_related('nomenklatura').order_by('-created_at')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @extend_schema(
        tags=['Nomenklatura'],
        summary="Nomenklatura uchun bir nechta rasm yuklash",
        description=(
            "Multipart form-data formatida bir nechta rasmni birdaniga yuklaydi. "
            "`nomenklatura` maydoniga `code_1c` qiymati yuboriladi."
        ),
        request=NomenklaturaImageBulkUploadSerializer,
        responses={
            201: OpenApiResponse(
                response=NomenklaturaImageSerializer(many=True),
                description="Yangi yuklangan rasmlar ro'yxati",
            ),
            400: OpenApiResponse(description="Kerakli maydonlar yetishmaydi"),
            404: OpenApiResponse(description="Nomenklatura topilmadi"),
        },
        examples=[
            OpenApiExample(
                name="Multipart sample",
                description="HTTPie yordamida bir nechta nomenklatura rasmini yuborish",
                value="http --form POST /api/v1/nomenklatura-images/bulk-upload/ nomenklatura=N-001 "
                "images@/path/img1.jpg images@/path/img2.jpg",
            )
        ],
    )
    @action(detail=False, methods=['post'], url_path='bulk-upload')
    def bulk_upload(self, request):
        """Bir vaqtda bir nechta rasm yuklash"""
        nomenklatura_code = request.data.get('nomenklatura')
        if not nomenklatura_code:
            return Response(
                {'error': 'nomenklatura code_1c talab qilinadi'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            nomenklatura = Nomenklatura.objects.get(code_1c=nomenklatura_code, is_deleted=False)
        except Nomenklatura.DoesNotExist:
            return Response(
                {'error': 'Nomenklatura topilmadi'},
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
            image_obj = NomenklaturaImage.objects.create(
                nomenklatura=nomenklatura,
                image=image,
                is_main=False,
                is_active=True,
                is_deleted=False
            )
            serializer = NomenklaturaImageSerializer(image_obj, context={'request': request})
            created_images.append(serializer.data)
        
        return Response({
            'message': f'{len(created_images)} ta rasm muvaffaqiyatli yuklandi',
            'images': created_images
        }, status=status.HTTP_201_CREATED)
