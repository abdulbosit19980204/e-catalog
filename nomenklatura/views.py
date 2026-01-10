import django_filters
from django.db.models import Q
from nomenklatura.models import Nomenklatura, NomenklaturaImage
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.cache import cache
from utils.cache import smart_cache_get, smart_cache_set, smart_cache_delete
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)
from openpyxl import load_workbook
from utils.excel import build_template_workbook, workbook_to_response, parse_bool_cell, clean_cell
from .serializers import (
    NomenklaturaImageBulkUploadSerializer,
    NomenklaturaImageSerializer,
    NomenklaturaSerializer,
)


class NomenklaturaFilterSet(django_filters.FilterSet):
    description_status = django_filters.ChoiceFilter(
        label="Description status",
        method="filter_description",
        choices=(("with", "Description bor"), ("without", "Description yo'q")),
    )
    image_status = django_filters.ChoiceFilter(
        label="Image status",
        method="filter_image_status",
        choices=(("with", "Rasm bor"), ("without", "Rasm yo'q")),
    )
    project = django_filters.CharFilter(field_name='projects__code_1c', label="Project code_1c")
    project_id = django_filters.NumberFilter(field_name='projects__id', label="Project ID")
    created_from = django_filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    created_to = django_filters.DateFilter(field_name='created_at', lookup_expr='date__lte')
    updated_from = django_filters.DateFilter(field_name='updated_at', lookup_expr='date__gte')
    updated_to = django_filters.DateFilter(field_name='updated_at', lookup_expr='date__lte')

    class Meta:
        model = Nomenklatura
        fields = ['code_1c', 'name', 'description_status', 'image_status', 'project', 'project_id', 'created_from', 'created_to', 'updated_from', 'updated_to', 'is_active', 'category']

    def filter_description(self, queryset, name, value):
        if value == "with":
            return queryset.exclude(Q(description__isnull=True) | Q(description__exact=""))
        if value == "without":
            return queryset.filter(Q(description__isnull=True) | Q(description__exact=""))
        return queryset

    def filter_image_status(self, queryset, name, value):
        if value == "with":
            # Rasmlari bor bo'lganlar
            return queryset.filter(images__is_deleted=False).distinct()
        if value == "without":
            # Rasmlari yo'q bo'lganlar
            return queryset.exclude(images__is_deleted=False).distinct()
        return queryset


class NomenklaturaImageFilterSet(django_filters.FilterSet):
    created_from = django_filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    created_to = django_filters.DateFilter(field_name='created_at', lookup_expr='date__lte')

    project = django_filters.CharFilter(field_name='nomenklatura__projects__code_1c', label="Project code_1c")
    project_id = django_filters.NumberFilter(field_name='nomenklatura__projects__id', label="Project ID")

    class Meta:
        model = NomenklaturaImage
        fields = ['nomenklatura', 'is_main', 'category', 'project', 'project_id', 'created_from', 'created_to']


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
            OpenApiParameter(
                name='description_status',
                required=False,
                type=OpenApiTypes.STR,
                description="Description bo'yicha filter (`with` | `without`)",
            ),
            OpenApiParameter(
                name='image_status',
                required=False,
                type=OpenApiTypes.STR,
                description="Rasm holati bo'yicha filter (`with` - rasm bor | `without` - rasm yo'q)",
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
                name='project',
                required=False,
                type=OpenApiTypes.STR,
                description="Project code_1c bo'yicha filter",
            ),
            OpenApiParameter(
                name='project_id',
                required=False,
                type=OpenApiTypes.INT,
                description="Project ID bo'yicha filter",
            ),
            OpenApiParameter(
                name='updated_to',
                required=False,
                type=OpenApiTypes.DATE,
                description="Yangilangan sana chegarasi (YYYY-MM-DD)",
            ),
            OpenApiParameter(
                name='is_active',
                required=False,
                type=OpenApiTypes.BOOL,
                description="Faol/Noaktivlik holati bo'yicha filter",
            ),
            OpenApiParameter(
                name='category',
                required=False,
                type=OpenApiTypes.STR,
                description="Kategoriya bo'yicha filter",
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
    filterset_class = NomenklaturaFilterSet
    search_fields = ['code_1c', 'name']
    
    def perform_create(self, serializer):
        super().perform_create(serializer)
        cache.clear()
        from django.core.cache import caches
        caches['fallback'].clear()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        cache.clear()
        from django.core.cache import caches
        caches['fallback'].clear()

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted', 'updated_at'])
        cache.clear()
        from django.core.cache import caches
        caches['fallback'].clear()
    
    def get_queryset(self):
        """Optimizatsiya: prefetch_related bilan images va projects yuklash - N+1 query muammosini hal qiladi"""
        cache_key = f"nomenklatura_queryset_{hash(str(self.request.query_params))}"
        cached_qs = smart_cache_get(cache_key)
        if cached_qs is None:
            qs = Nomenklatura.objects.filter(
                is_deleted=False
            ).prefetch_related(
                'images',
                'images__status',
                'images__source',
                'projects'
            ).order_by('-created_at')
            smart_cache_set(cache_key, qs, 300)
            return qs
        return cached_qs
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    # Excel helpers ---------------------------------------------------------
    @staticmethod
    def _nomenklatura_excel_headers():
        return [
            'code_1c', 'name', 'title', 'description', 'is_active',
            'sku', 'barcode', 'brand', 'manufacturer', 'model', 'series', 'vendor_code',
            'base_price', 'sale_price', 'cost_price', 'currency', 'discount_percent', 'tax_rate',
            'stock_quantity', 'min_stock', 'max_stock', 'unit_of_measure', 'weight', 'dimensions', 'volume',
            'category', 'subcategory',
            'color', 'size', 'material', 'warranty_period', 'expiry_date', 'production_date',
            'notes', 'rating', 'popularity_score', 'seo_keywords', 'source'
        ]

    def _validate_nomenklatura_headers(self, sheet):
        expected = [header.lower() for header in self._nomenklatura_excel_headers()]
        header_row = next(sheet.iter_rows(min_row=1, max_row=1, max_col=len(expected), values_only=True), None)
        if not header_row:
            return False, expected, []
        normalized = [clean_cell(value).lower() for value in header_row[:len(expected)]]
        return normalized == expected, expected, normalized

    @extend_schema(
        tags=['Nomenklatura'],
        summary="Nomenklatura ma'lumotlarini Excel formatda eksport qilish",
        responses={200: OpenApiResponse(description="XLSX fayl")},
    )
    @action(detail=False, methods=['get'], url_path='export-xlsx', permission_classes=[IsAuthenticated])
    def export_xlsx(self, request):
        # Export uchun alohida queryset - prefetch_related kerak emas va SQLite limit muammosini oldini oladi
        base_queryset = Nomenklatura.objects.filter(is_deleted=False)
        queryset = self.filter_queryset(base_queryset)
        
        workbook = build_template_workbook('Nomenklatura', self._nomenklatura_excel_headers())
        sheet = workbook.active
        
        # iterator() ishlatish - memory-efficient va SQLite limit muammosini hal qiladi
        # Chunking bilan ishlash - har safar 1000 ta yozuvni qayta ishlash
        chunk_size = 1000
        offset = 0
        
        while True:
            chunk = queryset[offset:offset + chunk_size]
            if not chunk.exists():
                break
            
            for item in chunk.iterator():
                sheet.append([
                    item.code_1c,
                    item.name,
                    item.title or '',
                    item.description or '',
                    item.is_active,
                    item.sku or '',
                    item.barcode or '',
                    item.brand or '',
                    item.manufacturer or '',
                    item.model or '',
                    item.series or '',
                    item.vendor_code or '',
                    item.base_price or '',
                    item.sale_price or '',
                    item.cost_price or '',
                    item.currency or '',
                    item.discount_percent or '',
                    item.tax_rate or '',
                    item.stock_quantity or '',
                    item.min_stock or '',
                    item.max_stock or '',
                    item.unit_of_measure or '',
                    item.weight or '',
                    item.dimensions or '',
                    item.volume or '',
                    item.category or '',
                    item.subcategory or '',
                    item.color or '',
                    item.size or '',
                    item.material or '',
                    item.warranty_period or '',
                    item.expiry_date.strftime('%Y-%m-%d') if item.expiry_date else '',
                    item.production_date.strftime('%Y-%m-%d') if item.production_date else '',
                    item.notes or '',
                    item.rating or '',
                    item.popularity_score or '',
                    item.seo_keywords or '',
                    item.source or '',
                ])
            
            offset += chunk_size
        
        return workbook_to_response(workbook, 'nomenklatura.xlsx')

    @extend_schema(
        tags=['Nomenklatura'],
        summary="Nomenklatura Excel shablonini yuklab olish",
        responses={200: OpenApiResponse(description="XLSX shablon fayl")},
    )
    @action(detail=False, methods=['get'], url_path='template-xlsx', permission_classes=[IsAuthenticated])
    def template_xlsx(self, request):
        workbook = build_template_workbook(
            'Nomenklatura template',
            self._nomenklatura_excel_headers(),
            ['NOM-001', 'Namuna mahsulot', 'Sarlavha', '<p>Izoh</p>', True],
        )
        return workbook_to_response(workbook, 'nomenklatura_template.xlsx')

    @extend_schema(
        tags=['Nomenklatura'],
        summary="Nomenklatura ma'lumotlarini Excel fayldan import qilish",
        request={
            'multipart/form-data': inline_serializer(
                name='NomenklaturaImportPayload',
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
        is_valid, expected, received = self._validate_nomenklatura_headers(sheet)
        if not is_valid:
            return Response(
                {'error': 'Excel headerlari mos emas', 'expected': expected, 'received': received},
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
                obj, created_flag = Nomenklatura.objects.update_or_create(
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

@extend_schema_view(
    list=extend_schema(
        tags=['Nomenklatura Image'],
        summary="Nomenklatura rasm ro'yxatini olish",
        description="Filtirlash: `nomenklatura` (ID), `category`, `project` (code_1c) yoki `project_id` orqali.",
        parameters=[
            OpenApiParameter(name="nomenklatura", type=OpenApiTypes.INT, description="Nomenklatura ID"),
            OpenApiParameter(name="project", type=OpenApiTypes.STR, description="Loyiha code_1c bo'yicha filtrlash"),
            OpenApiParameter(name="project_id", type=OpenApiTypes.INT, description="Loyiha ID bo'yicha filtrlash"),
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
    filterset_class = NomenklaturaImageFilterSet
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
            "`nomenklatura` maydoniga `code_1c` qiymati yuboriladi. Ixtiyoriy ravishda `category` "
            "va `note` maydonlari orqali rasmlarga umumiy teg yoki izoh qo'shish mumkin."
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
                "category=kir yuvish note='Telegram katalogi uchun' "
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

        category = request.data.get('category', '')
        note = request.data.get('note', '')
        
        created_images = []
        for image in images:
            image_obj = NomenklaturaImage.objects.create(
                nomenklatura=nomenklatura,
                image=image,
                is_main=False,
                is_active=True,
                is_deleted=False,
                category=category,
                note=note,
            )
            serializer = NomenklaturaImageSerializer(image_obj, context={'request': request})
            created_images.append(serializer.data)
        
        return Response({
            'message': f'{len(created_images)} ta rasm muvaffaqiyatli yuklandi',
            'images': created_images
        }, status=status.HTTP_201_CREATED)
