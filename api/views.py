import django_filters
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers, vary_on_cookie
from django.core.cache import cache
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from openpyxl import load_workbook
from client.models import ClientImage
from nomenklatura.models import NomenklaturaImage
from utils.excel import (
    build_template_workbook,
    clean_cell,
    parse_bool_cell,
    workbook_to_response,
)
from .models import Project, ProjectImage, ImageStatus, ImageSource, AgentLocation
from .serializers import (
    ProjectImageBulkUploadSerializer,
    ProjectImageSerializer,
    ProjectSerializer,
    ImageStatusSerializer,
    ImageSourceSerializer,
    ThumbnailEntrySerializer,
    AgentLocationSerializer,
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
        # Cache key based on filters
        cache_key = f"project_queryset_{hash(str(self.request.query_params))}"
        cached_qs = cache.get(cache_key)
        if cached_qs is None:
            qs = Project.objects.filter(
                is_deleted=False
            ).prefetch_related('images').order_by('-created_at')
            cache.set(cache_key, qs, 300)  # Cache for 5 minutes
            return qs
        return cached_qs
    
    @method_decorator(cache_page(300))  # Cache list view for 5 minutes
    @method_decorator(vary_on_headers('Authorization'))
    def list(self, request, *args, **kwargs):
        """Cached list view"""
        return super().list(request, *args, **kwargs)
    
    @method_decorator(cache_page(600))  # Cache detail view for 10 minutes
    def retrieve(self, request, *args, **kwargs):
        """Cached detail view"""
        return super().retrieve(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Invalidate cache on create"""
        super().perform_create(serializer)
        cache.clear()  # Clear all cache on create
    
    def perform_update(self, serializer):
        """Invalidate cache on update"""
        super().perform_update(serializer)
        cache.clear()  # Clear all cache on update
    
    def perform_destroy(self, instance):
        """Soft delete - projectni o'chirmasdan is_deleted=True qiladi"""
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted', 'updated_at'])
        cache.clear()  # Clear cache on delete
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_destroy(self, instance):
        """Soft delete - projectni o'chirmasdan is_deleted=True qiladi"""
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted', 'updated_at'])

    # Excel helpers ---------------------------------------------------------
    @staticmethod
    def _project_excel_headers():
        return ['code_1c', 'name', 'title', 'description', 'is_active']

    def _validate_project_headers(self, sheet):
        expected = [header.lower() for header in self._project_excel_headers()]
        header_row = next(sheet.iter_rows(min_row=1, max_row=1, max_col=len(expected), values_only=True), None)
        if not header_row:
            return False, expected, []
        normalized = [clean_cell(value).lower() for value in header_row[:len(expected)]]
        return normalized == expected, expected, normalized

    @extend_schema(
        tags=['Projects'],
        summary="Project ma'lumotlarini Excel formatida eksport qilish",
        description="Filtrlangan project ro'yxatini XLSX fayl sifatida qaytaradi.",
        responses={200: OpenApiResponse(description="XLSX fayl")},
    )
    @action(detail=False, methods=['get'], url_path='export-xlsx', permission_classes=[IsAuthenticated])
    def export_xlsx(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        workbook = build_template_workbook('Projects', self._project_excel_headers())
        sheet = workbook.active
        for project in queryset:
            sheet.append([
                project.code_1c,
                project.name,
                project.title or '',
                project.description or '',
                project.is_active,
            ])
        return workbook_to_response(workbook, 'projects.xlsx')

    @extend_schema(
        tags=['Projects'],
        summary="Project Excel shablonini yuklab olish",
        responses={200: OpenApiResponse(description="XLSX shablon fayl")},
    )
    @action(detail=False, methods=['get'], url_path='template-xlsx', permission_classes=[IsAuthenticated])
    def template_xlsx(self, request):
        workbook = build_template_workbook(
            'Projects template',
            self._project_excel_headers(),
            ['PRJ-001', 'Namuna project', 'Namuna sarlavha', '<p>Namuna description</p>', True],
        )
        return workbook_to_response(workbook, 'projects_template.xlsx')

    @extend_schema(
        tags=['Projects'],
        summary="Project ma'lumotlarini Excel fayldan import qilish",
        request={
            'multipart/form-data': inline_serializer(
                name='ProjectImportPayload',
                fields={
                    'file': serializers.FileField(help_text='XLSX fayl'),
                },
            )
        },
        responses={
            200: OpenApiResponse(description="Import natijalari (created/updated/errors)"),
            400: OpenApiResponse(description="Yaroqsiz fayl yoki header mos emas"),
        },
    )
    @action(
        detail=False,
        methods=['post'],
        url_path='import-xlsx',
        parser_classes=[MultiPartParser],
        permission_classes=[IsAuthenticated],
    )
    def import_xlsx(self, request):
        uploaded = request.FILES.get('file')
        if not uploaded:
            return Response({'error': 'file field talab qilinadi'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            workbook = load_workbook(uploaded, data_only=True)
        except Exception:
            return Response({'error': 'XLSX faylni o\'qib bo\'lmadi'}, status=status.HTTP_400_BAD_REQUEST)

        sheet = workbook.active
        is_valid, expected, received = self._validate_project_headers(sheet)
        if not is_valid:
            return Response(
                {
                    'error': 'Excel headerlari mos emas',
                    'expected': expected,
                    'received': received,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        stats = {'created': 0, 'updated': 0, 'errors': []}
        for idx, row in enumerate(
            sheet.iter_rows(min_row=2, max_col=len(expected), values_only=True),
            start=2,
        ):
            if not row or all(value in (None, '') for value in row):
                continue
            code = clean_cell(row[0])
            if not code:
                stats['errors'].append(f"Row {idx}: code_1c bo'sh bo'lishi mumkin emas")
                continue
            name = clean_cell(row[1]) or code
            title = clean_cell(row[2]) or None
            description = row[3] if row[3] is not None else ''
            is_active = parse_bool_cell(row[4], default=True)

            defaults = {
                'name': name,
                'title': title,
                'description': description,
                'is_active': is_active,
                'is_deleted': False,
            }
            try:
                obj, created_flag = Project.objects.update_or_create(
                    code_1c=code,
                    defaults=defaults,
                )
                if created_flag:
                    stats['created'] += 1
                else:
                    stats['updated'] += 1
            except Exception as exc:  # noqa: BLE001
                stats['errors'].append(f"Row {idx}: {exc}")
        return Response(stats, status=status.HTTP_200_OK)


class AgentLocationFilterSet(django_filters.FilterSet):
    date_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    date_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = AgentLocation
        fields = ['agent_code', 'region', 'platform', 'device_id', 'date_from', 'date_to']


@extend_schema_view(
    list=extend_schema(
        tags=['Agent Locations'],
        summary="Agent lokatsiya yozuvlari ro'yxati",
        description=(
            "Mobil agentlar tomonidan yuborilgan geolokatsiya yozuvlarini qaytaradi. "
            "Barcha maydonlar ixtiyoriy (majburiy emas). "
            "Qurilma, lokatsiya, tarmoq, sensor va boshqa ma'lumotlar bilan birga saqlanadi."
        ),
        parameters=[
            OpenApiParameter(name='agent_code', type=OpenApiTypes.STR, description="Agent kodi bo'yicha filter"),
            OpenApiParameter(name='region', type=OpenApiTypes.STR, description="Hudud bo'yicha filter"),
            OpenApiParameter(name='platform', type=OpenApiTypes.STR, description="Mobil platforma bo'yicha filter (Android/iOS)"),
            OpenApiParameter(name='device_id', type=OpenApiTypes.STR, description="Qurilma ID bo'yicha filter"),
            OpenApiParameter(name='date_from', type=OpenApiTypes.DATETIME, description="Yaratilgan vaqtdan boshlab"),
            OpenApiParameter(name='date_to', type=OpenApiTypes.DATETIME, description="Yaratilgan vaqtgacha"),
        ],
    ),
    create=extend_schema(
        tags=['Agent Locations'],
        summary="Agent lokatsiyasini yaratish",
        description=(
            "Mobil agent ilovasi lokatsiya ma'lumotlarini yuboradi. "
            "Barcha maydonlar ixtiyoriy, faqat `agent_code`, `latitude` va `longitude` majburiy. "
            "Qo'shimcha ma'lumotlar: qurilma (manufacturer, model, RAM, storage, camera), "
            "lokatsiya (city, country, timezone), tarmoq (WiFi, cellular, IP), "
            "sensorlar (accelerometer, gyroscope, magnetometer), "
            "batareya (level, health, temperature), "
            "xavfsizlik (fingerprint, encryption, screen lock) va boshqalar."
        ),
        request=inline_serializer(
            name='AgentLocationCreate',
            fields={
                'agent_code': serializers.CharField(required=True, help_text="Agent kodi (majburiy)"),
                'latitude': serializers.DecimalField(required=True, max_digits=9, decimal_places=6, help_text="Latitude (majburiy)"),
                'longitude': serializers.DecimalField(required=True, max_digits=9, decimal_places=6, help_text="Longitude (majburiy)"),
                'agent_name': serializers.CharField(required=False, allow_blank=True, help_text="Agent ismi"),
                'agent_phone': serializers.CharField(required=False, allow_blank=True, help_text="Agent telefoni"),
                'region': serializers.CharField(required=False, allow_blank=True, help_text="Hudud"),
                'device_id': serializers.CharField(required=False, allow_blank=True, help_text="Qurilma ID"),
                'device_name': serializers.CharField(required=False, allow_blank=True, help_text="Qurilma nomi"),
                'device_manufacturer': serializers.CharField(required=False, allow_blank=True, help_text="Ishlab chiqaruvchi"),
                'device_model': serializers.CharField(required=False, allow_blank=True, help_text="Qurilma modeli"),
                'platform': serializers.CharField(required=False, allow_blank=True, help_text="OS (Android/iOS)"),
                'os_version': serializers.CharField(required=False, allow_blank=True, help_text="OS versiyasi"),
                'screen_width': serializers.IntegerField(required=False, allow_null=True, help_text="Ekran kengligi (px)"),
                'screen_height': serializers.IntegerField(required=False, allow_null=True, help_text="Ekran balandligi (px)"),
                'screen_density': serializers.DecimalField(required=False, allow_null=True, max_digits=5, decimal_places=2, help_text="Ekran zichligi (DPI)"),
                'ram_total': serializers.IntegerField(required=False, allow_null=True, help_text="Jami RAM (byte)"),
                'ram_available': serializers.IntegerField(required=False, allow_null=True, help_text="Mavjud RAM (byte)"),
                'storage_total': serializers.IntegerField(required=False, allow_null=True, help_text="Jami xotira (byte)"),
                'storage_available': serializers.IntegerField(required=False, allow_null=True, help_text="Mavjud xotira (byte)"),
                'camera_front': serializers.BooleanField(required=False, help_text="Old kamera mavjudligi"),
                'camera_back': serializers.BooleanField(required=False, help_text="Orqa kamera mavjudligi"),
                'camera_resolution': serializers.CharField(required=False, allow_blank=True, help_text="Kamera o'lchami"),
                'app_version': serializers.CharField(required=False, allow_blank=True, help_text="Ilova versiyasi"),
                'app_build_number': serializers.CharField(required=False, allow_blank=True, help_text="Build raqami"),
                'app_installation_date': serializers.DateTimeField(required=False, allow_null=True, help_text="O'rnatilgan sana"),
                'app_last_update': serializers.DateTimeField(required=False, allow_null=True, help_text="Oxirgi yangilanish"),
                'accuracy': serializers.DecimalField(required=False, allow_null=True, max_digits=7, decimal_places=2, help_text="Aniqlik (m)"),
                'altitude': serializers.DecimalField(required=False, allow_null=True, max_digits=8, decimal_places=2, help_text="Balandlik (m)"),
                'speed': serializers.DecimalField(required=False, allow_null=True, max_digits=6, decimal_places=2, help_text="Tezlik (m/s)"),
                'heading': serializers.DecimalField(required=False, allow_null=True, max_digits=6, decimal_places=2, help_text="Yo'nalish (gradus)"),
                'city': serializers.CharField(required=False, allow_blank=True, help_text="Shahar"),
                'country': serializers.CharField(required=False, allow_blank=True, help_text="Davlat"),
                'postal_code': serializers.CharField(required=False, allow_blank=True, help_text="Pochta indeksi"),
                'timezone': serializers.CharField(required=False, allow_blank=True, help_text="Vaqt mintaqasi"),
                'location_provider': serializers.CharField(required=False, allow_blank=True, help_text="Lokatsiya manbasi"),
                'battery_level': serializers.DecimalField(required=False, allow_null=True, max_digits=4, decimal_places=1, help_text="Batareya (%)"),
                'is_charging': serializers.BooleanField(required=False, help_text="Batareya zaryadlanayaptimi"),
                'battery_health': serializers.CharField(required=False, allow_blank=True, help_text="Batareya holati"),
                'battery_temperature': serializers.DecimalField(required=False, allow_null=True, max_digits=5, decimal_places=2, help_text="Batareya harorati (°C)"),
                'battery_voltage': serializers.DecimalField(required=False, allow_null=True, max_digits=6, decimal_places=3, help_text="Batareya kuchlanishi (V)"),
                'signal_strength': serializers.CharField(required=False, allow_blank=True, help_text="Signal kuchi"),
                'network_type': serializers.CharField(required=False, allow_blank=True, help_text="Tarmoq turi"),
                'wifi_ssid': serializers.CharField(required=False, allow_blank=True, help_text="WiFi SSID"),
                'wifi_bssid': serializers.CharField(required=False, allow_blank=True, help_text="WiFi BSSID"),
                'cellular_operator': serializers.CharField(required=False, allow_blank=True, help_text="Mobil operator"),
                'cellular_network_type': serializers.CharField(required=False, allow_blank=True, help_text="Mobil tarmoq turi"),
                'ip_address': serializers.IPAddressField(required=False, allow_null=True, help_text="IP manzil"),
                'connection_type': serializers.CharField(required=False, allow_blank=True, help_text="Ulanish turi"),
                'accelerometer_x': serializers.DecimalField(required=False, allow_null=True, max_digits=8, decimal_places=4, help_text="Accelerometer X"),
                'accelerometer_y': serializers.DecimalField(required=False, allow_null=True, max_digits=8, decimal_places=4, help_text="Accelerometer Y"),
                'accelerometer_z': serializers.DecimalField(required=False, allow_null=True, max_digits=8, decimal_places=4, help_text="Accelerometer Z"),
                'gyroscope_x': serializers.DecimalField(required=False, allow_null=True, max_digits=8, decimal_places=4, help_text="Gyroscope X"),
                'gyroscope_y': serializers.DecimalField(required=False, allow_null=True, max_digits=8, decimal_places=4, help_text="Gyroscope Y"),
                'gyroscope_z': serializers.DecimalField(required=False, allow_null=True, max_digits=8, decimal_places=4, help_text="Gyroscope Z"),
                'magnetometer_x': serializers.DecimalField(required=False, allow_null=True, max_digits=8, decimal_places=4, help_text="Magnetometer X"),
                'magnetometer_y': serializers.DecimalField(required=False, allow_null=True, max_digits=8, decimal_places=4, help_text="Magnetometer Y"),
                'magnetometer_z': serializers.DecimalField(required=False, allow_null=True, max_digits=8, decimal_places=4, help_text="Magnetometer Z"),
                'proximity_sensor': serializers.DecimalField(required=False, allow_null=True, max_digits=8, decimal_places=4, help_text="Proximity sensor"),
                'light_sensor': serializers.DecimalField(required=False, allow_null=True, max_digits=8, decimal_places=2, help_text="Yorug'lik sensori"),
                'temperature': serializers.DecimalField(required=False, allow_null=True, max_digits=5, decimal_places=2, help_text="Harorat (°C)"),
                'humidity': serializers.DecimalField(required=False, allow_null=True, max_digits=5, decimal_places=2, help_text="Namlik (%)"),
                'pressure': serializers.DecimalField(required=False, allow_null=True, max_digits=7, decimal_places=2, help_text="Bosim (hPa)"),
                'device_fingerprint': serializers.CharField(required=False, allow_blank=True, help_text="Qurilma fingerprint"),
                'is_rooted': serializers.BooleanField(required=False, help_text="Root qilinganmi"),
                'is_jailbroken': serializers.BooleanField(required=False, help_text="Jailbreak qilinganmi"),
                'encryption_enabled': serializers.BooleanField(required=False, help_text="Shifrlash yoqilganmi"),
                'screen_lock_type': serializers.CharField(required=False, allow_blank=True, help_text="Ekran qulfi turi"),
                'logged_at': serializers.DateTimeField(required=False, allow_null=True, help_text="Qurilmada yozilgan vaqt"),
                'address': serializers.CharField(required=False, allow_blank=True, help_text="Manzil"),
                'note': serializers.CharField(required=False, allow_blank=True, help_text="Izoh"),
                'metadata': serializers.JSONField(required=False, allow_null=True, help_text="Qo'shimcha JSON ma'lumotlar"),
            }
        ),
    ),
    retrieve=extend_schema(
        tags=['Agent Locations'],
        summary="Bitta lokatsiya yozuvini olish",
        description="Barcha maydonlar bilan birga lokatsiya yozuvini qaytaradi."
    ),
    update=extend_schema(
        tags=['Agent Locations'],
        summary="Lokatsiya yozuvini to'liq yangilash",
    ),
    partial_update=extend_schema(
        tags=['Agent Locations'],
        summary="Lokatsiya yozuvini qisman yangilash",
    ),
    destroy=extend_schema(tags=['Agent Locations'], summary="Lokatsiya yozuvini soft-delete qilish"),
)
class AgentLocationViewSet(viewsets.ModelViewSet):
    queryset = AgentLocation.objects.filter(is_deleted=False)
    serializer_class = AgentLocationSerializer
    filterset_class = AgentLocationFilterSet
    permission_classes = [IsAuthenticated]
    search_fields = ['agent_code', 'agent_name', 'agent_phone', 'device_id', 'device_name', 'region']
    ordering = ['-created_at']

    def get_queryset(self):
        return AgentLocation.objects.filter(is_deleted=False).order_by('-created_at')

    def perform_destroy(self, instance):
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
    """ImageStatus CRUD operatsiyalari - Heavily cached"""
    queryset = ImageStatus.objects.filter(is_deleted=False, is_active=True)
    serializer_class = ImageStatusSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Statuslar kam bo'ladi, pagination kerak emas
    search_fields = ['code', 'name', 'description']
    ordering = ['order', 'name']
    
    @method_decorator(cache_page(3600))  # Cache for 1 hour (rarely changes)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @method_decorator(cache_page(3600))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        super().perform_create(serializer)
        cache.clear()
    
    def perform_update(self, serializer):
        super().perform_update(serializer)
        cache.clear()
    
    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        cache.clear()


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
@method_decorator(cache_page(180), name='get')  # Cache for 3 minutes
class ThumbnailFeedView(ThumbnailFeedMixin, APIView):
    """Birlashtirilgan thumbnail feed (project/client/nomenklatura) - Cached"""

    permission_classes = [AllowAny]

    def get(self, request):
        # Cache key based on query parameters
        cache_key = f"thumbnail_feed_{hash(str(request.query_params))}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data, status=status.HTTP_200_OK)
        
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
        response_data = serialized.data
        
        # Cache the response
        cache.set(cache_key, response_data, 180)  # 3 minutes
        
        return Response(response_data, status=status.HTTP_200_OK)


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
