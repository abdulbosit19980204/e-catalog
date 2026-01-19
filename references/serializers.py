from rest_framework import serializers
from .models import VisitType, VisitStatus, VisitPriority, VisitStep

class VisitTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitType
        fields = ['id', 'code', 'name', 'sort_order', 'description']


class VisitStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitStatus
        fields = ['id', 'code', 'name', 'color', 'sort_order', 'is_final']


class VisitPrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitPriority
        fields = ['id', 'code', 'name', 'level', 'color']


class VisitStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitStep
        fields = ['id', 'project', 'title', 'description', 'input_type', 'is_required', 'sort_order']
