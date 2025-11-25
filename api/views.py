import django_filters
from django.db.models import Q
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from client.models import ClientImage
from nomenklatura.models import NomenklaturaImage
from .models import Project, ProjectImage, ImageStatus, ImageSource
from .serializers import (
    ProjectImageBulkUploadSerializer,
    ProjectImageSerializer,
    ProjectSerializer,
    ImageStatusSerializer,
    ImageSourceSerializer,
    ThumbnailEntrySerializer,
)


class ProjectFilterSet(django_filters.FilterSet):
    description_status = django_filters.ChoiceFilter(
        label="Description status",
        method="filter_description",
        choices=(("with", "Description bor"), ("without", "Description yo'q")),
    )
    created_from = django_filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    created_to = django_filters.DateFilter(field_name='created_at', lookup_expr='date__lte')
    updated_from = django_filters.DateFilter(field_name='updated_at', lookup_expr='date__gte')
    updated_to = django_filters.DateFilter(field_name='updated_at', lookup_expr='date__lte')

    class Meta:
        model = Project
        fields = ['code_1c', 'name', 'description_status', 'created_from', 'created_to', 'updated_from', 'updated_to']

    def filter_description(self, queryset, name, value):
        if value == "with":
            return queryset.exclude(Q(description__isnull=True) | Q(description__exact=""))
        if value == "without":
            return queryset.filter(Q(description__isnull=True) | Q(description__exact=""))
        return queryset


class ProjectImageFilterSet(django_filters.FilterSet):
    created_from = django_filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    created_to = django_filters.DateFilter(field_name='created_at', lookup_expr='date__lte')

    class Meta:
        model = ProjectImage
        fields = ['project', 'is_main', 'category', 'created_from', 'created_to']


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
            OpenApiParameter(
                name='description_status',
                required=False,
                type=OpenApiTypes.STR,
                description="Description bo'yicha filter (`with` | `without`)",
            ),
            OpenApiParameter(
                name='created_from',
                required=False,
                type=OpenApiTypes.DATE,
                description="Yaratilgan sanadan boshlab (YYYY-MM-DD)",
            ),
            OpenApiParameter(
                name='created_to',
                required=False,
                type=OpenApiTypes.DATE,
                description="Yaratilgan sana chegarasi (YYYY-MM-DD)",
            ),
            OpenApiParameter(
                name='updated_from',
                required=False,
                type=OpenApiTypes.DATE,
                description="Yangilangan sanadan boshlab (YYYY-MM-DD)",
            ),
            OpenApiParameter(
                name='updated_to',
                required=False,
                type=OpenApiTypes.DATE,
                description="Yangilangan sana chegarasi (YYYY-MM-DD)",
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
    filterset_class = ProjectFilterSet
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
            OpenApiParameter(
                name='category',
                required=False,
                type=OpenApiTypes.STR,
                description="Rasm toifasi bo'yicha filter",
            ),
            OpenApiParameter(
                name='created_from',
                required=False,
                type=OpenApiTypes.DATE,
                description="Yaratilgan sanadan boshlab (YYYY-MM-DD)",
            ),
            OpenApiParameter(
                name='created_to',
                required=False,
                type=OpenApiTypes.DATE,
                description="Yaratilgan sana chegarasi (YYYY-MM-DD)",
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
    filterset_class = ProjectImageFilterSet
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
            "`project` maydoniga `code_1c` qiymati, `images` maydoniga esa bir yoki bir nechta fayl yuboriladi. "
            "Ixtiyoriy ravishda `category` va `note` maydonlari orqali rasmlar uchun umumiy teg yoki izoh qo'shish mumkin."
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
                "category=marketing note='Banner versiyasi' "
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

        category = request.data.get('category', '')
        note = request.data.get('note', '')
        
        created_images = []
        for image in images:
            image_obj = ProjectImage.objects.create(
                project=project,
                image=image,
                is_main=False,
                is_active=True,
                is_deleted=False,
                category=category,
                note=note,
            )
            serializer = ProjectImageSerializer(image_obj, context={'request': request})
            created_images.append(serializer.data)
        
        return Response({
            'message': f'{len(created_images)} ta rasm muvaffaqiyatli yuklandi',
            'images': created_images
        }, status=status.HTTP_201_CREATED)


@extend_schema_view(
    list=extend_schema(
        tags=['Image Management'],
        summary="Image statuslar ro'yxatini olish",
        description="Barcha aktiv image statuslar ro'yxatini qaytaradi. Pagination yo'q.",
    ),
    retrieve=extend_schema(
        tags=['Image Management'],
        summary="Bitta image status ma'lumotini olish",
    ),
    create=extend_schema(
        tags=['Image Management'],
        summary="Yangi image status yaratish",
    ),
    update=extend_schema(
        tags=['Image Management'],
        summary="Image status ma'lumotlarini to'liq yangilash",
    ),
    partial_update=extend_schema(
        tags=['Image Management'],
        summary="Image status ma'lumotlarini qisman yangilash",
    ),
    destroy=extend_schema(
        tags=['Image Management'],
        summary="Image status'ni soft-delete qilish",
    ),
)
class ImageStatusViewSet(viewsets.ModelViewSet):
    """ImageStatus CRUD operatsiyalari"""
    queryset = ImageStatus.objects.filter(is_deleted=False, is_active=True)
    serializer_class = ImageStatusSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Statuslar kam bo'ladi, pagination kerak emas
    search_fields = ['code', 'name', 'description']
    ordering = ['order', 'name']


@extend_schema_view(
    list=extend_schema(
        tags=['Image Management'],
        summary="Image source ro'yxatini olish",
        description="Barcha aktiv image source'lar ro'yxatini pagination bilan qaytaradi.",
    ),
    retrieve=extend_schema(
        tags=['Image Management'],
        summary="Bitta image source ma'lumotini olish",
    ),
    create=extend_schema(
        tags=['Image Management'],
        summary="Yangi image source yaratish",
    ),
    update=extend_schema(
        tags=['Image Management'],
        summary="Image source ma'lumotlarini to'liq yangilash",
    ),
    partial_update=extend_schema(
        tags=['Image Management'],
        summary="Image source ma'lumotlarini qisman yangilash",
    ),
    destroy=extend_schema(
        tags=['Image Management'],
        summary="Image source'ni soft-delete qilish",
    ),
)
class ImageSourceViewSet(viewsets.ModelViewSet):
    """ImageSource CRUD operatsiyalari"""
    queryset = ImageSource.objects.filter(is_deleted=False)
    serializer_class = ImageSourceSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['uploader_name', 'uploader_contact', 'upload_location']
    ordering = ['-created_at']


class ThumbnailFeedMixin:
    """Reusable helper mixin for thumbnail responses"""

    @staticmethod
    def _parse_entity_types(raw: str | None):
        allowed = ['project', 'client', 'nomenklatura']
        if not raw:
            return allowed
        parsed = []
        for part in raw.split(','):
            trimmed = part.strip().lower()
            if trimmed in allowed and trimmed not in parsed:
                parsed.append(trimmed)
        return parsed or allowed

    @staticmethod
    def _parse_limit(raw: str | None) -> int:
        default = 60
        max_limit = 200
        if raw is None:
            return default
        try:
            value = int(raw)
            if value < 1:
                return default
            return min(value, max_limit)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _parse_bool(raw: str | None):
        if raw is None:
            return None
        return raw.strip().lower() in ('1', 'true', 'yes')

    def _collect_project_thumbnails(self, request, limit, is_main, status_code):
        qs = ProjectImage.objects.filter(
            is_deleted=False,
            is_active=True,
            project__is_deleted=False,
        ).select_related('project', 'status', 'source').order_by('-created_at')
        if is_main is not None:
            qs = qs.filter(is_main=is_main)
        if status_code:
            qs = qs.filter(status__code=status_code)
        qs = qs[:limit]
        return [
            self._build_entry(
                request,
                entity_type='project',
                entity=image.project,
                image=image,
                code_attr='code_1c'
            )
            for image in qs
        ]

    def _collect_client_thumbnails(self, request, limit, is_main, status_code):
        qs = ClientImage.objects.filter(
            is_deleted=False,
            is_active=True,
            client__is_deleted=False,
        ).select_related('client', 'status', 'source').order_by('-created_at')
        if is_main is not None:
            qs = qs.filter(is_main=is_main)
        if status_code:
            qs = qs.filter(status__code=status_code)
        qs = qs[:limit]
        return [
            self._build_entry(
                request,
                entity_type='client',
                entity=image.client,
                image=image,
                code_attr='client_code_1c'
            )
            for image in qs
        ]

    def _collect_nomenklatura_thumbnails(self, request, limit, is_main, status_code):
        qs = NomenklaturaImage.objects.filter(
            is_deleted=False,
            is_active=True,
            nomenklatura__is_deleted=False,
        ).select_related('nomenklatura', 'status', 'source').order_by('-created_at')
        if is_main is not None:
            qs = qs.filter(is_main=is_main)
        if status_code:
            qs = qs.filter(status__code=status_code)
        qs = qs[:limit]
        return [
            self._build_entry(
                request,
                entity_type='nomenklatura',
                entity=image.nomenklatura,
                image=image,
                code_attr='code_1c'
            )
            for image in qs
        ]

    def _build_entry(self, request, entity_type, entity, image, code_attr):
        status_obj = getattr(image, 'status', None)
        source_obj = getattr(image, 'source', None)
        code_value = getattr(entity, code_attr, None)
        if not code_value:
            code_value = ''
        return {
            'entity_type': entity_type,
            'entity_id': entity.id,
            'code_1c': code_value,
            'entity_name': getattr(entity, 'name', str(entity)),
            'image_id': image.id,
            'thumbnail_url': self._absolute_url(request, image),
            'is_main': image.is_main,
            'category': image.category or None,
            'note': image.note or None,
            'status_code': status_obj.code if status_obj else None,
            'status_name': status_obj.name if status_obj else None,
            'source_name': source_obj.uploader_name if source_obj else None,
            'source_type': source_obj.uploader_type if source_obj else None,
            'created_at': image.created_at,
        }

    @staticmethod
    def _absolute_url(request, image_obj):
        try:
            thumb = image_obj.image_thumbnail
        except Exception:  # noqa: BLE001 - imagekit throws RuntimeError when image absent
            return None
        if not thumb:
            return None
        url = thumb.url
        if not request:
            return url
        return request.build_absolute_uri(url)


@extend_schema(
    tags=['Image Management'],
    summary="Birlashtirilgan thumbnail feed",
    description=(
        "Project, Client va Nomenklatura rasmlarining faqat thumbnail URL larini qaytaradi. "
        "Har bir element entity haqida identifikatsion ma'lumotlar (ID, code, nom) bilan birga keladi. "
        "Endpoint mobil yoki frontend ilovasi uchun tezkor rasm previewlarini olishga mo'ljallangan."
    ),
    parameters=[
        OpenApiParameter(
            name='entity_type',
            type=OpenApiTypes.STR,
            required=False,
            description="Filtrlash uchun entity turlari (virgullar bilan ajratilgan). "
                        "Ruxsat etilgan qiymatlar: project, client, nomenklatura. Default: hammasi.",
        ),
        OpenApiParameter(
            name='is_main',
            type=OpenApiTypes.BOOL,
            required=False,
            description="Faqat asosiy (true) yoki oddiy (false) rasmlarni qaytarish",
        ),
        OpenApiParameter(
            name='status',
            type=OpenApiTypes.STR,
            required=False,
            description="ImageStatus kodi bo'yicha filter (masalan: store_before)",
        ),
        OpenApiParameter(
            name='limit',
            type=OpenApiTypes.INT,
            required=False,
            description="Qaytariladigan maksimal elementlar soni (default: 60, max: 200)",
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=ThumbnailEntrySerializer(many=True),
            description="Thumbnail feed ma'lumotlari",
        )
    }
)
class ThumbnailFeedView(ThumbnailFeedMixin, APIView):
    """Birlashtirilgan thumbnail feed (project/client/nomenklatura)"""

    permission_classes = [AllowAny]

    def get(self, request):
        requested_types = self._parse_entity_types(request.query_params.get('entity_type'))
        limit = self._parse_limit(request.query_params.get('limit'))
        is_main = self._parse_bool(request.query_params.get('is_main'))
        status_code = request.query_params.get('status')

        per_type_limit = max(limit, 1)
        entries = []

        if 'project' in requested_types:
            entries.extend(
                self._collect_project_thumbnails(request, per_type_limit, is_main, status_code)
            )
        if 'client' in requested_types:
            entries.extend(
                self._collect_client_thumbnails(request, per_type_limit, is_main, status_code)
            )
        if 'nomenklatura' in requested_types:
            entries.extend(
                self._collect_nomenklatura_thumbnails(request, per_type_limit, is_main, status_code)
            )

        entries.sort(key=lambda item: item['created_at'], reverse=True)
        serialized = ThumbnailEntrySerializer(entries[:limit], many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Image Management'],
    summary="Project thumbnail rasmlari",
    description="Faqat `ProjectImage` larining thumbnail URL larini qaytaradi.",
    parameters=[
        OpenApiParameter(
            name='is_main',
            type=OpenApiTypes.BOOL,
            required=False,
            description="Faqat asosiy (true) yoki oddiy (false) rasmlarni qaytarish",
        ),
        OpenApiParameter(
            name='status',
            type=OpenApiTypes.STR,
            required=False,
            description="ImageStatus kodi bo'yicha filter (masalan: store_before)",
        ),
        OpenApiParameter(
            name='limit',
            type=OpenApiTypes.INT,
            required=False,
            description="Qaytariladigan maksimal elementlar soni (default: 60, max: 200)",
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=ThumbnailEntrySerializer(many=True),
            description="Project thumbnail ma'lumotlari",
        )
    }
)
class ProjectThumbnailView(ThumbnailFeedMixin, APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        limit = self._parse_limit(request.query_params.get('limit'))
        is_main = self._parse_bool(request.query_params.get('is_main'))
        status_code = request.query_params.get('status')

        entries = self._collect_project_thumbnails(request, limit, is_main, status_code)
        serialized = ThumbnailEntrySerializer(entries, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Image Management'],
    summary="Client thumbnail rasmlari",
    description="Faqat `ClientImage` larining thumbnail URL larini qaytaradi.",
    parameters=[
        OpenApiParameter(
            name='is_main',
            type=OpenApiTypes.BOOL,
            required=False,
            description="Faqat asosiy (true) yoki oddiy (false) rasmlarni qaytarish",
        ),
        OpenApiParameter(
            name='status',
            type=OpenApiTypes.STR,
            required=False,
            description="ImageStatus kodi bo'yicha filter (masalan: store_before)",
        ),
        OpenApiParameter(
            name='limit',
            type=OpenApiTypes.INT,
            required=False,
            description="Qaytariladigan maksimal elementlar soni (default: 60, max: 200)",
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=ThumbnailEntrySerializer(many=True),
            description="Client thumbnail ma'lumotlari",
        )
    }
)
class ClientThumbnailView(ThumbnailFeedMixin, APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        limit = self._parse_limit(request.query_params.get('limit'))
        is_main = self._parse_bool(request.query_params.get('is_main'))
        status_code = request.query_params.get('status')

        entries = self._collect_client_thumbnails(request, limit, is_main, status_code)
        serialized = ThumbnailEntrySerializer(entries, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Image Management'],
    summary="Nomenklatura thumbnail rasmlari",
    description="Faqat `NomenklaturaImage` larining thumbnail URL larini qaytaradi.",
    parameters=[
        OpenApiParameter(
            name='is_main',
            type=OpenApiTypes.BOOL,
            required=False,
            description="Faqat asosiy (true) yoki oddiy (false) rasmlarni qaytarish",
        ),
        OpenApiParameter(
            name='status',
            type=OpenApiTypes.STR,
            required=False,
            description="ImageStatus kodi bo'yicha filter (masalan: store_before)",
        ),
        OpenApiParameter(
            name='limit',
            type=OpenApiTypes.INT,
            required=False,
            description="Qaytariladigan maksimal elementlar soni (default: 60, max: 200)",
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=ThumbnailEntrySerializer(many=True),
            description="Nomenklatura thumbnail ma'lumotlari",
        )
    }
)
class NomenklaturaThumbnailView(ThumbnailFeedMixin, APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        limit = self._parse_limit(request.query_params.get('limit'))
        is_main = self._parse_bool(request.query_params.get('is_main'))
        status_code = request.query_params.get('status')

        entries = self._collect_nomenklatura_thumbnails(request, limit, is_main, status_code)
        serialized = ThumbnailEntrySerializer(entries, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)
