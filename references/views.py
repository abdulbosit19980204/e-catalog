from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import VisitType, VisitStatus, VisitPriority, VisitStep
from .serializers import (
    VisitTypeSerializer, 
    VisitStatusSerializer, 
    VisitPrioritySerializer,
    VisitStepSerializer
)

class VisitTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List of available visit types
    """
    queryset = VisitType.objects.all()
    serializer_class = VisitTypeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None


class VisitStatusViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List of available visit statuses
    """
    queryset = VisitStatus.objects.all()
    serializer_class = VisitStatusSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None


class VisitPriorityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List of available visit priorities
    """
    queryset = VisitPriority.objects.all()
    serializer_class = VisitPrioritySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None


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
