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
from .models import Project, ProjectImage
from .serializers import (
    ProjectSerializer,
    ProjectImageSerializer,
    ProjectImageBulkUploadSerializer,
)


@extend_schema_view(
    list=extend_schema(
        tags=['Projects'],
        summary="Project ro'yxatini olish",
        description=(
            "Aktiv va soft-delete qilinmagan project'lar ro'yxatini pagination bilan qaytaradi."
            " `search` parametri orqali nom, title va `code_1c` bo'yicha qidirish mumkin."
        ),
        parameters=[
            OpenApiParameter(
                name='search',
                required=False,
                type=OpenApiTypes.STR,
                description="Project nomi, title yoki code_1c bo'yicha qidirish",
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
                description="Aniq code_1c bo'yicha filter",
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
        tags=['Projects'],
        summary="Bitta project ma'lumotini olish",
        description="`code_1c` identifikatoriga ko'ra project ma'lumotlarini qaytaradi.",
    ),
    create=extend_schema(
        tags=['Projects'],
        summary="Project yaratish",
        description="Yangi project yozuvini yaratadi. `code_1c` unikal bo'lishi kerak.",
    ),
    update=extend_schema(
        tags=['Projects'],
        summary="Project ma'lumotlarini to'liq yangilash",
        description="`PUT` so'rovi butun project yozuvini yangilaydi.",
    ),
    partial_update=extend_schema(
        tags=['Projects'],
        summary="Project ma'lumotlarini qisman yangilash",
        description="Faqat yuborilgan maydonlarni yangilaydi. `code_1c` o'zgarmaydi.",
    ),
    destroy=extend_schema(
        tags=['Projects'],
        summary="Project'ni soft-delete qilish",
        description="Yozuvni `is_deleted=True` qilib belgilaydi va ro'yxatdan yashiradi.",
        responses={204: OpenApiResponse(description="Project soft-delete qilindi")},
    ),
)
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.filter(is_deleted=False)
    serializer_class = ProjectSerializer
    lookup_field = 'code_1c'
    filterset_fields = ['code_1c', 'name']
    search_fields = ['code_1c', 'name', 'title']
    
    def get_queryset(self):
        """Optimizatsiya: prefetch_related bilan images yuklash - N+1 query muammosini hal qiladi"""
        return Project.objects.filter(
            is_deleted=False
        ).prefetch_related('images').order_by('-created_at')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_destroy(self, instance):
        """Soft delete - projectni o'chirmasdan is_deleted=True qiladi"""
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted', 'updated_at'])

@extend_schema_view(
    list=extend_schema(
        tags=['Projects'],
        summary="Project rasmlari ro'yxatini olish",
        description="`project` va `is_main` bo'yicha filterlash mumkin.",
        parameters=[
            OpenApiParameter(
                name='project',
                required=False,
                type=OpenApiTypes.STR,
                description="Project code_1c bo'yicha filter",
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
        tags=['Projects'],
        summary="Project uchun bitta rasm yuklash",
        description="Multipart form-data orqali bitta rasm faylini yuklaydi.",
    ),
    destroy=extend_schema(
        tags=['Projects'],
        summary="Project rasmini o'chirish",
        description="Rasmni soft-delete qiladi yoki bazadan o'chiradi.",
    ),
)
class ProjectImageViewSet(viewsets.ModelViewSet):
    queryset = ProjectImage.objects.filter(is_deleted=False)
    serializer_class = ProjectImageSerializer
    filterset_fields = ['project', 'is_main']
    search_fields = ['project__code_1c', 'project__name']
    
    def get_queryset(self):
        """Optimizatsiya: select_related bilan project yuklash - N+1 query muammosini hal qiladi"""
        return ProjectImage.objects.filter(
            is_deleted=False
        ).select_related('project').order_by('-created_at')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @extend_schema(
        tags=['Projects'],
        summary="Project uchun bir nechta rasm yuklash",
        description=(
            "Multipart form-data formatida bir nechta rasmni birdaniga yuklash imkonini beradi. "
            "`project` maydoniga `code_1c` qiymati, `images` maydoniga esa bir yoki bir nechta fayl yuboriladi."
        ),
        request=ProjectImageBulkUploadSerializer,
        responses={
            201: OpenApiResponse(
                response=ProjectImageSerializer(many=True),
                description="Yangi yuklangan rasmlar ro'yxati",
            ),
            400: OpenApiResponse(description="Kerakli maydonlar yetishmaydi"),
            404: OpenApiResponse(description="Project topilmadi"),
        },
        examples=[
            OpenApiExample(
                name="Multipart sample",
                description="HTTPie yordamida bir nechta rasm yuborish",
                value="http --form POST /api/v1/project-images/bulk-upload/ project=P-001 "
                "images@/path/to/image1.jpg images@/path/to/image2.jpg",
            )
        ],
    )
    @action(detail=False, methods=['post'], url_path='bulk-upload')
    def bulk_upload(self, request):
        """Bir vaqtda bir nechta rasm yuklash"""
        project_code = request.data.get('project')
        if not project_code:
            return Response(
                {'error': 'project code_1c talab qilinadi'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            project = Project.objects.get(code_1c=project_code, is_deleted=False)
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project topilmadi'},
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
            image_obj = ProjectImage.objects.create(
                project=project,
                image=image,
                is_main=False,
                is_active=True,
                is_deleted=False
            )
            serializer = ProjectImageSerializer(image_obj, context={'request': request})
            created_images.append(serializer.data)
        
        return Response({
            'message': f'{len(created_images)} ta rasm muvaffaqiyatli yuklandi',
            'images': created_images
        }, status=status.HTTP_201_CREATED)
