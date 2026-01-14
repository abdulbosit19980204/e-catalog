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
    agent = django_filters.CharFilter(field_name='agent_code', lookup_expr='iexact')
    client = django_filters.CharFilter(field_name='client_code', lookup_expr='iexact')
    
    class Meta:
        model = Visit
        fields = ['visit_type', 'visit_status', 'priority', 'agent_code', 'client_code']


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
    update=extend_schema(
        tags=['Visits'],
        summary="Tashrif yangilash",
        description="Tashrif ma'lumotlarini yangilash"
    ),
    partial_update=extend_schema(
        tags=['Visits'],
        summary="Qisman yangilash",
        description="Faqat ba'zi maydonlarni yangilash"
    ),
    destroy=extend_schema(
        tags=['Visits'],
        summary="Tashrif o'chirish",
        description="Tashrifni soft-delete qilish"
    ),
)
class VisitViewSet(viewsets.ModelViewSet):
    """
    Visit Management ViewSet
    Full CRUD + custom actions for visit lifecycle management
    """
    permission_classes = [IsAuthenticated]
    filterset_class = VisitFilter
    search_fields = ['agent_name', 'client_name', 'purpose', 'notes']
    ordering_fields = ['planned_date', 'created_at', 'actual_start_time']
    ordering = ['-planned_date', '-planned_time']
    
    def get_queryset(self):
        """Optimized queryset with prefetch"""
        return Visit.objects.filter(
            is_deleted=False
        ).select_related().prefetch_related('images').order_by('-planned_date')
    
    def get_serializer_class(self):
        """Dynamic serializer selection"""
        if self.action == 'list':
            return VisitListSerializer
        elif self.action == 'create':
            return VisitCreateSerializer
        return VisitDetailSerializer
    
    def perform_destroy(self, instance):
        """Soft delete"""
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted', 'updated_at'])
    
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
        
        # Validate status
        if visit.visit_status not in ['SCHEDULED', 'CONFIRMED']:
            return Response(
                {'error': 'Faqat rejalashtirilgan tashriflarga check-in qilish mumkin'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = VisitCheckInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Perform check-in
        visit.check_in(
            latitude=serializer.validated_data['latitude'],
            longitude=serializer.validated_data['longitude'],
            accuracy=serializer.validated_data.get('accuracy')
        )
        
        if 'address' in serializer.validated_data:
            visit.check_in_address = serializer.validated_data['address']
            visit.save(update_fields=['check_in_address'])
        
        return Response(
            VisitDetailSerializer(visit).data,
            status=status.HTTP_200_OK
        )
    
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
        
        # Update visit details
        data = serializer.validated_data
        visit.check_out(
            latitude=data.get('latitude'),
            longitude=data.get('longitude')
        )
        
        # Update other fields
        if 'tasks_completed' in data:
            visit.tasks_completed = data['tasks_completed']
        if 'outcome' in data:
            visit.outcome = data['outcome']
        if 'notes' in data:
            visit.notes = data['notes']
        if 'client_satisfaction' in data:
            visit.client_satisfaction = data['client_satisfaction']
        if 'next_visit_date' in data:
            visit.next_visit_date = data['next_visit_date']
        if 'next_visit_notes' in data:
            visit.next_visit_notes = data['next_visit_notes']
        
        visit.save()
        
        return Response(
            VisitDetailSerializer(visit).data,
            status=status.HTTP_200_OK
        )
    
    @extend_schema(
        tags=['Visits'],
        summary="Rasm yuklash",
        description="Tashrif davomida rasm yuklash",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'image': {'type': 'string', 'format': 'binary'},
                    'image_type': {'type': 'string'},
                    'notes': {'type': 'string'},
                }
            }
        },
        responses={201: VisitImageSerializer}
    )
    @action(detail=True, methods=['post'], url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload image during visit"""
        visit = self.get_object()
        
        # This is a placeholder - actual image upload logic would go here
        # You would integrate with your image storage service
        
        return Response(
            {'message': 'Image upload endpoint - integrate with your storage'},
            status=status.HTTP_501_NOT_IMPLEMENTED
        )
    
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
class VisitPlanViewSet(viewsets.ModelViewSet):
    """Visit Plan Management"""
    queryset = VisitPlan.objects.filter(is_deleted=False)
    serializer_class = VisitPlanSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['agent_code', 'client_code', 'is_active', 'frequency']
    ordering = ['agent_code', 'planned_weekday', 'planned_time']
    
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
        """Auto-generate visits from active plans"""
        created_count = 0
        
        active_plans = VisitPlan.objects.filter(
            is_active=True,
            auto_generate=True,
            is_deleted=False
        )
        
        for plan in active_plans:
            # Logic to generate visits from plan
            # This would check if visit already exists and create if not
            # Placeholder for now
            pass
        
        return Response({'created': created_count})


class VisitImageViewSet(viewsets.ModelViewSet):
    """Visit Images Management"""
    queryset = VisitImage.objects.filter(is_deleted=False)
    serializer_class = VisitImageSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['visit', 'image_type']
    ordering = ['-captured_at']
    
    def perform_destroy(self, instance):
        """Soft delete"""
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted', 'updated_at'])
