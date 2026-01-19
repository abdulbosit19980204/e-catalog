"""
Visit Management API Views
High-performance ViewSets with comprehensive actions
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg, Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
import django_filters

from django.core.cache import cache
from utils.cache import smart_cache_get, smart_cache_set, smart_cache_delete
from .models import Visit, VisitPlan, VisitImage
from .serializers import (
    VisitListSerializer, VisitDetailSerializer, VisitCreateSerializer,
    VisitCheckInSerializer, VisitCheckOutSerializer, VisitCancelSerializer,
    VisitPlanSerializer, VisitImageSerializer, VisitStatisticsSerializer
)


class VisitFilter(django_filters.FilterSet):
    """Advanced filtering for visits"""
    date_from = django_filters.DateFilter(field_name='planned_date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='planned_date', lookup_expr='lte')
    agent_code = django_filters.CharFilter(field_name='agent_code', lookup_expr='iexact')
    client_code = django_filters.CharFilter(field_name='client_code', lookup_expr='iexact')
    agent = django_filters.NumberFilter(field_name='agent__id')
    client = django_filters.NumberFilter(field_name='client__id')
    search = django_filters.CharFilter(method='filter_search', label="Search")

    class Meta:
        model = Visit
        fields = ['visit_type', 'visit_status', 'priority', 'agent', 'client', 'agent_code', 'client_code']

    def filter_search(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(agent_name__icontains=value) |
                Q(client_name__icontains=value) |
                Q(agent__user__first_name__icontains=value) |
                Q(client__name__icontains=value) |
                Q(purpose__icontains=value) |
                Q(notes__icontains=value)
            )
        return queryset


from utils.mixins import ProjectScopedMixin

@extend_schema_view(
    list=extend_schema(
        tags=['Visits'],
        summary="Tashrif ro'yxati",
        description="Barcha tashriflarni filtrlash va qidirish imkoniyati bilan",
        parameters=[
            OpenApiParameter('agent_code', OpenApiTypes.STR, description="Agent kodi"),
            OpenApiParameter('client_code', OpenApiTypes.STR, description="Klient kodi"),
            OpenApiParameter('visit_status', OpenApiTypes.STR, description="Status"),
            OpenApiParameter('date_from', OpenApiTypes.DATE, description="Boshlanish sanasi"),
            OpenApiParameter('date_to', OpenApiTypes.DATE, description="Tugash sanasi"),
        ]
    ),
    retrieve=extend_schema(
        tags=['Visits'],
        summary="Tashrif tafsilotlari",
        description="Bitta tashrifning to'liq ma'lumotlari va rasmlari"
    ),
    create=extend_schema(
        tags=['Visits'],
        summary="Yangi tashrif yaratish",
        description="Yangi tashrif rejasini yaratish (admin/supervisor uchun)"
    ),
)
class VisitViewSet(ProjectScopedMixin, viewsets.ModelViewSet):
    """
    Visit Management ViewSet
    Optimized with ProjectScopedMixin for data isolation
    """
    from utils.pagination import OptionalLimitOffsetPagination
    
    permission_classes = [IsAuthenticated]
    filterset_class = VisitFilter
    pagination_class = OptionalLimitOffsetPagination
    search_fields = ['agent_name', 'client_name', 'purpose', 'notes']
    ordering_fields = ['planned_date', 'created_at', 'actual_start_time']
    ordering = ['-planned_date', '-planned_time']
    
    def get_queryset(self):
        """Optimized queryset with parent-scoped and prefetch"""
        # Mixin filters by project
        queryset = super().get_queryset().filter(is_deleted=False)
        queryset = queryset.prefetch_related('images').order_by('-planned_date', '-planned_time')
        return queryset

    def _resolve_links(self, instance):
        """Helper to resolve agent and client links by their codes"""
        from users.models import UserProfile
        from client.models import Client
        
        # Link Agent (UserProfile)
        if instance.agent_code and not instance.agent:
            agent_profile = UserProfile.objects.filter(code_1c=instance.agent_code, is_deleted=False).first()
            if agent_profile:
                instance.agent = agent_profile
                # Also sync names/phones if they are currently custom/empty
                if not instance.agent_name:
                    instance.agent_name = agent_profile.user.get_full_name() or agent_profile.user.username
                
        # Link Client
        if instance.client_code and not instance.client:
            client_obj = Client.objects.filter(client_code_1c=instance.client_code, is_deleted=False).first()
            if client_obj:
                instance.client = client_obj
                if not instance.client_name:
                    instance.client_name = client_obj.name
                if not instance.client_address:
                    instance.client_address = client_obj.actual_address or ""

        instance.save()

    def perform_create(self, serializer):
        # Mixin handles project assignment
        instance = serializer.save()
        self._resolve_links(instance)
        cache.clear()

    def perform_update(self, serializer):
        instance = serializer.save()
        self._resolve_links(instance)
        cache.clear()

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted', 'updated_at'])
        cache.clear()
    
    def get_serializer_class(self):
        """Dynamic serializer selection"""
        if self.action == 'list':
            return VisitListSerializer
        elif self.action == 'create':
            return VisitCreateSerializer
        elif self.action == 'upload_image':
            return VisitImageSerializer
        return VisitDetailSerializer
    
    @extend_schema(
        tags=['Visits'],
        summary="Check-in (Tashrif boshlash)",
        description="Tashrif joyiga yetib check-in qilish. GPS koordinatalar kerak.",
        request=VisitCheckInSerializer,
        responses={200: VisitDetailSerializer}
    )
    @action(detail=True, methods=['post'], url_path='check-in')
    def check_in(self, request, pk=None):
        """Check in to visit location"""
        visit = self.get_object()
        
        if visit.visit_status not in ['SCHEDULED', 'CONFIRMED']:
            return Response(
                {'error': 'Faqat rejalashtirilgan tashriflarga check-in qilish mumkin'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = VisitCheckInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        visit.check_in(
            latitude=serializer.validated_data['latitude'],
            longitude=serializer.validated_data['longitude'],
            accuracy=serializer.validated_data.get('accuracy')
        )
        
        if 'address' in serializer.validated_data:
            visit.check_in_address = serializer.validated_data['address']
            visit.save(update_fields=['check_in_address'])
        
        # Trigger Sync with 1C
        from .services import VisitSyncService
        VisitSyncService.sync_visit(visit, status_type='check_in')
        
        return Response(VisitDetailSerializer(visit).data)
    
    @extend_schema(
        tags=['Visits'],
        summary="Check-out (Tashrif yakunlash)",
        description="Tashrifni yakunlash va natijalarni saqlash",
        request=VisitCheckOutSerializer,
        responses={200: VisitDetailSerializer}
    )
    @action(detail=True, methods=['post'], url_path='check-out')
    def check_out(self, request, pk=None):
        """Complete visit and save outcomes"""
        visit = self.get_object()
        
        if visit.visit_status != 'IN_PROGRESS':
            return Response(
                {'error': 'Faqat jarayondagi tashriflarga check-out qilish mumkin'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = VisitCheckOutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        visit.check_out(
            latitude=data.get('latitude'),
            longitude=data.get('longitude')
        )
        
        # Update other fields
        for field in ['tasks_completed', 'outcome', 'notes', 'client_satisfaction', 'next_visit_date', 'next_visit_notes']:
            if field in data:
                setattr(visit, field, data[field])
        
        visit.save()

        # Trigger Sync with 1C
        from .services import VisitSyncService
        VisitSyncService.sync_visit(visit, status_type='check_out')

        return Response(VisitDetailSerializer(visit).data)
    
    @extend_schema(
        tags=['Visits'],
        summary="Rasm yuklash",
        description="Tashrif davomida rasm yuklash",
        request=VisitImageSerializer,
        responses={201: VisitImageSerializer}
    )
    @action(detail=True, methods=['post'], url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload image during visit"""
        visit = self.get_object()
        serializer = VisitImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Save nested image object
        serializer.save(visit=visit)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        tags=['Visits'],
        summary="Tashrif bekor qilish",
        description="Rejalashtirilgan tashrifni bekor qilish",
        request=VisitCancelSerializer,
        responses={200: VisitDetailSerializer}
    )
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_visit(self, request, pk=None):
        """Cancel scheduled visit"""
        visit = self.get_object()
        
        if visit.visit_status == 'COMPLETED':
            return Response(
                {'error': 'Yakunlangan tashrifni bekor qilib bo\'lmaydi'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = VisitCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        visit.cancel(
            reason=serializer.validated_data['reason'],
            cancelled_by=serializer.validated_data['cancelled_by']
        )
        
        return Response(
            VisitDetailSerializer(visit).data,
            status=status.HTTP_200_OK
        )
    
    @extend_schema(
        tags=['Visits'],
        summary="Tashrif statistikasi",
        description="Agent yoki klient uchun tashrif statistikasi",
        parameters=[
            OpenApiParameter('agent_code', OpenApiTypes.STR),
            OpenApiParameter('client_code', OpenApiTypes.STR),
            OpenApiParameter('date_from', OpenApiTypes.DATE),
            OpenApiParameter('date_to', OpenApiTypes.DATE),
        ],
        responses={200: VisitStatisticsSerializer}
    )
    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        """Get visit statistics"""
        # Apply filters
        queryset = Visit.objects.filter(is_deleted=False)
        
        agent_code = request.query_params.get('agent_code')
        client_code = request.query_params.get('client_code')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if agent_code:
            queryset = queryset.filter(agent_code=agent_code)
        if client_code:
            queryset = queryset.filter(client_code=client_code)
        if date_from:
            queryset = queryset.filter(planned_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(planned_date__lte=date_to)
        
        # Calculate statistics
        total = queryset.count()
        completed = queryset.filter(visit_status='COMPLETED').count()
        in_progress = queryset.filter(visit_status='IN_PROGRESS').count()
        cancelled = queryset.filter(visit_status='CANCELLED').count()
        
        # Calculate averages
        avg_duration = queryset.filter(
            visit_status='COMPLETED',
            duration_minutes__isnull=False
        ).aggregate(avg=Avg('duration_minutes'))['avg'] or 0
        
        # Image count
        total_images = VisitImage.objects.filter(
            visit__in=queryset,
            is_deleted=False
        ).count()
        
        stats = {
            'total_visits': total,
            'completed_visits': completed,
            'in_progress_visits': in_progress,
            'cancelled_visits': cancelled,
            'completion_rate': round((completed / total * 100) if total > 0 else 0, 2),
            'average_duration': round(avg_duration, 2),
            'total_images': total_images
        }
        
        serializer = VisitStatisticsSerializer(stats)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        tags=['Visit Plans'],
        summary="Tashrif rejalari ro'yxati",
        description="Barcha takrorlanuvchi tashrif rejalarini ko'rish"
    ),
    create=extend_schema(
        tags=['Visit Plans'],
        summary="Yangi reja yaratish",
        description="Takrorlanuvchi tashrif rejasini yaratish"
    ),
)
class VisitPlanViewSet(ProjectScopedMixin, viewsets.ModelViewSet):
    """Visit Plan Management"""
    queryset = VisitPlan.objects.filter(is_deleted=False)
    serializer_class = VisitPlanSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['agent_code', 'client_code', 'is_active', 'frequency']
    ordering = ['agent_code', 'planned_weekday', 'planned_time']
    
    def _resolve_links(self, instance):
        """Helper to resolve agent and client links by their codes"""
        from users.models import UserProfile
        from client.models import Client
        
        # Link Agent (UserProfile)
        if instance.agent_code and not instance.agent:
            agent_profile = UserProfile.objects.filter(code_1c=instance.agent_code, is_deleted=False).first()
            if agent_profile:
                instance.agent = agent_profile
                
        # Link Client
        if instance.client_code and not instance.client:
            client_obj = Client.objects.filter(client_code_1c=instance.client_code, is_deleted=False).first()
            if client_obj:
                instance.client = client_obj

        instance.save()

    def perform_create(self, serializer):
        instance = serializer.save()
        self._resolve_links(instance)

    def perform_update(self, serializer):
        instance = serializer.save()
        self._resolve_links(instance)

    def perform_destroy(self, instance):
        """Soft delete"""
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted', 'updated_at'])
    
    @extend_schema(
        tags=['Visit Plans'],
        summary="Haftalik tashriflar yaratish",
        description="Rejadan keyingi haftaga tashriflar avtomatik yaratish",
        responses={200: {'type': 'object', 'properties': {'created': {'type': 'integer'}}}}
    )
    @action(detail=False, methods=['post'], url_path='generate-weekly')
    def generate_weekly(self, request):
        """Auto-generate visits from active plans for the upcoming week"""
        from datetime import date, timedelta
        created_count = 0
        
        # Define the target week (next week)
        today = date.today()
        # Find next Monday
        next_monday = today + timedelta(days=(7 - today.weekday()))
        
        active_plans = self.get_queryset().filter(
            is_active=True,
            auto_generate=True
        ).select_related('agent', 'client', 'agent__user', 'project')
        
        for plan in active_plans:
            # 0=Monday, ..., 6=Sunday
            target_date = next_monday + timedelta(days=plan.planned_weekday)
            
            # Check if visit already exists
            exists = Visit.objects.filter(
                project=plan.project,
                agent_code=plan.agent_code,
                client_code=plan.client_code,
                planned_date=target_date,
                is_deleted=False
            ).exists()
            
            if not exists:
                # Use details from linked entities if available
                agent_name = plan.agent.user.get_full_name() if plan.agent else f"Agent {plan.agent_code}"
                client_name = plan.client.name if plan.client else f"Client {plan.client_code}"
                client_address = plan.client.actual_address if plan.client else ""
                
                Visit.objects.create(
                    project=plan.project,
                    agent=plan.agent,
                    client=plan.client,
                    agent_code=plan.agent_code,
                    client_code=plan.client_code,
                    agent_name=agent_name,
                    client_name=client_name,
                    client_address=client_address,
                    visit_type='PLANNED',
                    visit_status='SCHEDULED',
                    priority=plan.priority,
                    planned_date=target_date,
                    planned_time=plan.planned_time,
                    planned_duration_minutes=plan.duration_minutes
                )
                created_count += 1
        
        return Response({'created': created_count})


class VisitImageViewSet(ProjectScopedMixin, viewsets.ModelViewSet):
    """Visit Images Management"""
    queryset = VisitImage.objects.filter(is_deleted=False)
    serializer_class = VisitImageSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['visit', 'image_type']
    ordering = ['-captured_at']
    
    # Custom get_queryset to ensure image's visit belongs to the project
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return queryset
        
        # Verify the visit of this image belongs to user's project
        return queryset.filter(visit__project=user.profile.project)

    def perform_destroy(self, instance):
        """Soft delete"""
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted', 'updated_at'])
