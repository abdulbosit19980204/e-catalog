from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import VisitType, VisitStatus, VisitPriority, VisitStep
from .serializers import (
    VisitTypeSerializer, 
    VisitStatusSerializer, 
    VisitPrioritySerializer,
    VisitStepSerializer
)

from drf_spectacular.utils import extend_schema, OpenApiExample

@extend_schema(
    tags=['References'],
    summary="Tashrif turlari",
    description="Mavjud tashrif turlari ro'yxati (Masalan: Planli, Boshqa)"
)
class VisitTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List of available visit types
    """
    queryset = VisitType.objects.all()
    serializer_class = VisitTypeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None


@extend_schema(
    tags=['References'],
    summary="Tashrif statuslari",
    description="Tashrif holatlari (Masalan: SCHEDULED, IN_PROGRESS, COMPLETED)"
)
class VisitStatusViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List of available visit statuses
    """
    queryset = VisitStatus.objects.all()
    serializer_class = VisitStatusSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None


@extend_schema(
    tags=['References'],
    summary="Tashrif prioritetlari",
    description="Muhimlik darajalari (High, Medium, Low)"
)
class VisitPriorityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List of available visit priorities
    """
    queryset = VisitPriority.objects.all()
    serializer_class = VisitPrioritySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None


@extend_schema(
    tags=['References'],
    summary="Tashrif qadamlari (Checklist)",
    description="Tashrif davomida bajarilishi kerak bo'lgan vazifalar shablonlari",
    examples=[
         OpenApiExample(
            "Step Create (Checkbox)",
            value={
                "title": "Mahsulotlar joyida ekanligini tekshirish",
                "description": "Polkada barcha mahsulotlar borligini tasdiqlang",
                "input_type": "checkbox",
                "is_required": True,
                "sort_order": 1
            },
            request_only=True
        ),
        OpenApiExample(
            "Step Create (Photo)",
            value={
                "title": "Polka rasmi",
                "description": "Asosiy vitrina rasmini oling",
                "input_type": "photo",
                "is_required": True,
                "sort_order": 2
            },
            request_only=True
        )
    ]
)
class VisitStepViewSet(viewsets.ModelViewSet):
    """
    Manage visit steps (Tasks)
    """
    queryset = VisitStep.objects.all()
    serializer_class = VisitStepSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter steps by project if needed"""
        queryset = super().get_queryset()
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(models.Q(project_id=project_id) | models.Q(project__isnull=True))
        return queryset
