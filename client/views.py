import django_filters
from django.db.models import Q
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
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
from .models import Client, ClientImage
from .serializers import ClientImageBulkUploadSerializer, ClientImageSerializer, ClientSerializer


class ClientFilterSet(django_filters.FilterSet):
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
    project = django_filters.CharFilter(field_name='project__code_1c', label="Project code_1c")
    project_id = django_filters.NumberFilter(field_name='project__id', label="Project ID")
    created_from = django_filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    created_to = django_filters.DateFilter(field_name='created_at', lookup_expr='date__lte')
    updated_from = django_filters.DateFilter(field_name='updated_at', lookup_expr='date__gte')
    updated_to = django_filters.DateFilter(field_name='updated_at', lookup_expr='date__lte')

    class Meta:
        model = Client
        fields = [
            'client_code_1c',
            'name',
            'email',
            'project',
            'project_id',
            'created_from',
            'created_to',
            'updated_from',
            'updated_to',
            'is_active',
        ]

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


class ClientImageFilterSet(django_filters.FilterSet):
    client_code_1c = django_filters.CharFilter(field_name='client__client_code_1c')
    created_from = django_filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    created_to = django_filters.DateFilter(field_name='created_at', lookup_expr='date__lte')

    class Meta:
        model = ClientImage
        fields = ['client', 'client_code_1c', 'is_main', 'category', 'created_from', 'created_to']


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
                name='updated_to',
                required=False,
                type=OpenApiTypes.DATE,
                description="Yangilangan sana chegarasi (YYYY-MM-DD)",
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
    lookup_value_regex = '.+'
    filterset_class = ClientFilterSet
    search_fields = ['client_code_1c', 'name', 'email']
    permission_classes = [IsAuthenticated]  # Faqat authenticated user'lar uchun
    
    def get_queryset(self):
        """Optimizatsiya: prefetch_related bilan images yuklash - N+1 query muammosini hal qiladi"""
        return Client.objects.filter(
            is_deleted=False
        ).prefetch_related(
            'images',
            'images__status',
            'images__source'
        ).select_related('project').order_by('-created_at')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    # Excel helpers ---------------------------------------------------------
    @staticmethod
    def _client_excel_headers():
        return [
            'client_code_1c', 'name', 'email', 'phone', 'description', 'is_active',
            'company_name', 'tax_id', 'registration_number', 'legal_address', 'actual_address',
            'fax', 'website', 'industry', 'business_type', 'employee_count', 'annual_revenue',
            'established_date', 'payment_terms', 'credit_limit', 'currency',
            'city', 'region', 'country', 'postal_code',
            'contact_person', 'contact_position', 'contact_email', 'contact_phone',
            'notes', 'rating', 'priority', 'source'
        ]

    def _validate_client_headers(self, sheet):
        expected = [header.lower() for header in self._client_excel_headers()]
        header_row = next(sheet.iter_rows(min_row=1, max_row=1, max_col=len(expected), values_only=True), None)
        if not header_row:
            return False, expected, []
        normalized = [clean_cell(value).lower() for value in header_row[:len(expected)]]
        return normalized == expected, expected, normalized

    @extend_schema(
        tags=['Clients'],
        summary="Client ma'lumotlarini Excel formatda eksport qilish",
        responses={200: OpenApiResponse(description="XLSX fayl")},
    )
    @action(detail=False, methods=['get'], url_path='export-xlsx', permission_classes=[IsAuthenticated])
    def export_xlsx(self, request):
        # Export uchun alohida queryset - prefetch_related kerak emas va SQLite limit muammosini oldini oladi
        base_queryset = Client.objects.filter(is_deleted=False)
        queryset = self.filter_queryset(base_queryset)
        
        workbook = build_template_workbook('Clients', self._client_excel_headers())
        sheet = workbook.active
        
        # iterator() ishlatish - memory-efficient va SQLite limit muammosini hal qiladi
        # Chunking bilan ishlash - har safar 1000 ta yozuvni qayta ishlash
        chunk_size = 1000
        offset = 0
        
        while True:
            chunk = queryset[offset:offset + chunk_size]
            if not chunk.exists():
                break
            
            for client in chunk.iterator():
                sheet.append([
                    client.client_code_1c,
                    client.name,
                    client.email or '',
                    client.phone or '',
                    client.description or '',
                    client.is_active,
                    client.company_name or '',
                    client.tax_id or '',
                    client.registration_number or '',
                    client.legal_address or '',
                    client.actual_address or '',
                    client.fax or '',
                    client.website or '',
                    client.industry or '',
                    client.business_type or '',
                    client.employee_count or '',
                    client.annual_revenue or '',
                    client.established_date.strftime('%Y-%m-%d') if client.established_date else '',
                    client.payment_terms or '',
                    client.credit_limit or '',
                    client.currency or '',
                    client.city or '',
                    client.region or '',
                    client.country or '',
                    client.postal_code or '',
                    client.contact_person or '',
                    client.contact_position or '',
                    client.contact_email or '',
                    client.contact_phone or '',
                    client.notes or '',
                    client.rating or '',
                    client.priority or '',
                    client.source or '',
                ])
            
            offset += chunk_size
        
        return workbook_to_response(workbook, 'clients.xlsx')

    @extend_schema(
        tags=['Clients'],
        summary="Client Excel shablonini yuklab olish",
        responses={200: OpenApiResponse(description="XLSX shablon fayl")},
    )
    @action(detail=False, methods=['get'], url_path='template-xlsx', permission_classes=[IsAuthenticated])
    def template_xlsx(self, request):
        workbook = build_template_workbook(
            'Clients template',
            self._client_excel_headers(),
            ['CLI-001', 'Namuna client', 'client@example.com', '+998 90 000 00 00', 'Izoh', True],
        )
        return workbook_to_response(workbook, 'clients_template.xlsx')

    @extend_schema(
        tags=['Clients'],
        summary="Client ma'lumotlarini Excel fayldan import qilish",
        request={
            'multipart/form-data': inline_serializer(
                name='ClientImportPayload',
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
        is_valid, expected, received = self._validate_client_headers(sheet)
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
                stats['errors'].append(f"Row {idx}: client_code_1c bo'sh bo'lishi mumkin emas")
                continue
            name = clean_cell(row[1]) or code
            email = clean_cell(row[2]) or None
            phone = clean_cell(row[3]) or None
            description = row[4] if row[4] is not None else ''
            is_active = parse_bool_cell(row[5], default=True)

            defaults = {
                'name': name,
                'email': email or None,
                'phone': phone or None,
                'description': description,
                'is_active': is_active,
                'is_deleted': False,
            }
            try:
                obj, created_flag = Client.objects.update_or_create(
                    client_code_1c=code,
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
        tags=['Clients'],
        summary="Client rasmlari ro'yxatini olish",
        description="Client rasmlarini `client` (ID) va `client_code_1c` bo'yicha filterlash mumkin.",
        parameters=[
            OpenApiParameter(
                name='client',
                required=False,
                type=OpenApiTypes.INT,
                description="Client ID bo'yicha filter",
            ),
            OpenApiParameter(
                name='client_code_1c',
                required=False,
                type=OpenApiTypes.STR,
                description="Client client_code_1c bo'yicha filter",
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
    filterset_class = ClientImageFilterSet
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
            "`client` maydoniga `client_code_1c` qiymati yuboriladi. Ixtiyoriy ravishda "
            "`category` va `note` maydonlari orqali rasmlarga umumiy teg yoki izoh berish mumkin."
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
                "category=report note='Ishchi jarayon fotosi' "
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
        
        # Fix: get() o'rniga filter().first() ishlatamiz (duplicate code bo'lsa 500 xato bermasligi uchun)
        client = Client.objects.filter(client_code_1c=client_code, is_deleted=False).first()
        
        if not client:
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

        category = request.data.get('category', '')
        note = request.data.get('note', '')
        
        created_images = []
        for image in images:
            image_obj = ClientImage.objects.create(
                client=client,
                image=image,
                is_main=False,
                is_active=True,
                is_deleted=False,
                category=category,
                note=note,
            )
            serializer = ClientImageSerializer(image_obj, context={'request': request})
            created_images.append(serializer.data)
        
        return Response({
            'message': f'{len(created_images)} ta rasm muvaffaqiyatli yuklandi',
            'images': created_images
        }, status=status.HTTP_201_CREATED)
@extend_schema_view(
    list=extend_schema(
        tags=['Agent Visits'],
        summary="Agent tashrifi rasmlari ro'yxatini olish",
        description="Agentlar tomonidan magazinlarga tashrif buyurilganda olingan rasmlarni qaytaradi (millonlab recordlar uchun optimallashtirilgan).",
    ),
    create=extend_schema(
        tags=['Agent Visits'],
        summary="Tashrif rasmini yuklash",
        description="Agent tashrifi davomida olingan rasmni yuklash.",
    ),
)
class VisitImageViewSet(viewsets.ModelViewSet):
    """
    Agent tashriflari (visit) davomida olingan rasmlar uchun maxsus API.
    Millionlab recordlar uchun optimallashtirilgan.
    """
    queryset = ClientImage.objects.filter(is_deleted=False)
    serializer_class = ClientImageSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['client__name', 'client__client_code_1c', 'note']
    filterset_fields = ['client', 'status', 'is_main', 'category']

    def get_queryset(self):
        # Faqat kerakli maydonlarni yuklash orqali memory va I/O ni tejaymiz
        return ClientImage.objects.filter(
            is_deleted=False,
            # Faqat tashrifga aloqador statusdagi rasmlarni qaytaramiz (agar buni xoxlashsa)
            # status__code__in=['store_before', 'store_after'] 
        ).select_related(
            'client', 'status', 'source'
        ).only(
            'id', 'client__id', 'client__name', 'client__client_code_1c',
            'image', 'is_main', 'category', 'note', 'status', 'source',
            'created_at'
        ).order_by('-created_at')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
