"""
Visit Management Serializers
High-performance serializers with optimized queries
"""
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from .models import Visit, VisitPlan, VisitImage


class VisitImageSerializer(serializers.ModelSerializer):
    """Serializer for visit images"""
    
    class Meta:
        model = VisitImage
        fields = [
            'image_id', 'image_type', 'image_url', 'thumbnail_url',
            'captured_at', 'latitude', 'longitude', 'notes',
            'client_image_id'
        ]
        read_only_fields = ['image_id', 'captured_at']


class UserProfileTinySerializer(serializers.ModelSerializer):
    """Minimal user profile information"""
    username = serializers.CharField(source='user.username', read_only=True)
    full_name = serializers.CharField(source='user.first_name', read_only=True)
    
    class Meta:
        from users.models import UserProfile
        model = UserProfile
        fields = ['id', 'username', 'full_name', 'code_1c']


class ClientTinySerializer(serializers.ModelSerializer):
    """Minimal client information"""
    class Meta:
        from client.models import Client
        model = Client
        fields = ['id', 'name', 'client_code_1c', 'actual_address']


from references.models import VisitType, VisitStatus, VisitPriority

class VisitListSerializer(serializers.ModelSerializer):
    """Optimized serializer for list views"""
    image_count = serializers.SerializerMethodField()
    is_overdue = serializers.BooleanField(read_only=True)
    agent_details = UserProfileTinySerializer(source='agent', read_only=True)
    client_details = ClientTinySerializer(source='client', read_only=True)
    
    # Dynamic fields display as codes
    visit_type = serializers.SlugRelatedField(read_only=True, slug_field='code')
    status = serializers.SlugRelatedField(read_only=True, slug_field='code')
    priority = serializers.SlugRelatedField(read_only=True, slug_field='code')
    
    # Backward compatibility for 'visit_status'
    visit_status = serializers.CharField(source='status.code', read_only=True)
    
    class Meta:
        model = Visit
        fields = [
            'visit_id', 'agent', 'agent_details', 'agent_code', 'agent_name', 
            'client', 'client_details', 'client_code', 'client_name', 
            'visit_type', 'status', 'visit_status', 'priority',
            'planned_date', 'planned_time', 'actual_start_time',
            'actual_end_time', 'duration', 'image_count',
            'is_overdue', 'created_at'
        ]
        read_only_fields = ['visit_id', 'duration', 'created_at']
    
    @extend_schema_field(OpenApiTypes.INT)
    def get_image_count(self, obj):
        """Get number of images for this visit"""
        return obj.images.filter(is_deleted=False).count()


from .models import VisitStepResult

class VisitStepResultSerializer(serializers.ModelSerializer):
    """Serializer for visit step results"""
    step_title = serializers.CharField(source='step.title', read_only=True)
    step_description = serializers.CharField(source='step.description', read_only=True)
    step_type = serializers.CharField(source='step.input_type', read_only=True)
    step_required = serializers.BooleanField(source='step.is_required', read_only=True)
    
    class Meta:
        model = VisitStepResult
        fields = [
            'id', 'step', 'step_title', 'step_description', 'step_type', 'step_required',
            'value_text', 'value_number', 'value_boolean', 'value_photo',
            'is_completed', 'completed_at'
        ]
        read_only_fields = ['id', 'step', 'completed_at']


class VisitDetailSerializer(serializers.ModelSerializer):
    """Full serializer with all details and nested images"""
    images = VisitImageSerializer(many=True, read_only=True)
    step_results = VisitStepResultSerializer(many=True, read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    is_in_progress = serializers.BooleanField(read_only=True)
    agent_details = UserProfileTinySerializer(source='agent', read_only=True)
    client_details = ClientTinySerializer(source='client', read_only=True)
    
    visit_type = serializers.SlugRelatedField(read_only=True, slug_field='code')
    status = serializers.SlugRelatedField(read_only=True, slug_field='code')
    priority = serializers.SlugRelatedField(read_only=True, slug_field='code')
    
    visit_status = serializers.CharField(source='status.code', read_only=True)
    
    class Meta:
        model = Visit
        fields = '__all__'
        read_only_fields = [
            'visit_id', 'duration', 'created_at', 'updated_at',
            'cancelled_at'
        ]


class VisitCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new visits"""
    
    visit_type = serializers.SlugRelatedField(
        slug_field='code', 
        queryset=VisitType.objects.all(),
        required=False
    )
    priority = serializers.SlugRelatedField(
        slug_field='code', 
        queryset=VisitPriority.objects.all(), 
        required=False
    )
    # Status is usually set automatically, but if needed:
    status = serializers.SlugRelatedField(
        slug_field='code', 
        queryset=VisitStatus.objects.all(), 
        required=False
    )

    class Meta:
        model = Visit
        fields = [
            'agent_code', 'agent_name', 'agent_phone',
            'client_code', 'client_name', 'client_address',
            'visit_type', 'priority', 'status', 'planned_date', 'planned_time',
            'planned_duration_minutes', 'purpose'
        ]
    
    def validate_planned_date(self, value):
        """Ensure planned date is not in the past"""
        from django.utils import timezone
        if value < timezone.now().date():
            raise serializers.ValidationError(
                "Tashrif sanasi o'tmishda bo'lishi mumkin emas"
            )
        return value


class VisitCheckInSerializer(serializers.Serializer):
    """Serializer for check-in action"""
    latitude = serializers.DecimalField(max_digits=10, decimal_places=7)
    longitude = serializers.DecimalField(max_digits=10, decimal_places=7)
    accuracy = serializers.FloatField(required=False, allow_null=True)
    address = serializers.CharField(required=False, allow_blank=True)


class VisitCheckOutSerializer(serializers.Serializer):
    """Serializer for check-out action"""
    latitude = serializers.DecimalField(
        max_digits=10, decimal_places=7,
        required=False, allow_null=True
    )
    longitude = serializers.DecimalField(
        max_digits=10, decimal_places=7,
        required=False, allow_null=True
    )
    tasks_completed = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    outcome = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    client_satisfaction = serializers.IntegerField(
        min_value=1, max_value=5,
        required=False, allow_null=True
    )
    next_visit_date = serializers.DateField(required=False, allow_null=True)
    next_visit_notes = serializers.CharField(required=False, allow_blank=True)


class VisitCancelSerializer(serializers.Serializer):
    """Serializer for cancel action"""
    reason = serializers.CharField()
    cancelled_by = serializers.CharField()


class VisitPlanSerializer(serializers.ModelSerializer):
    """Serializer for visit plans"""
    
    class Meta:
        model = VisitPlan
        fields = '__all__'
        read_only_fields = ['plan_id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate plan configuration"""
        if data.get('end_date') and data.get('start_date'):
            if data['end_date'] < data['start_date']:
                raise serializers.ValidationError({
                    'end_date': "Tugash sanasi boshlanish sanasidan katta bo'lishi kerak"
                })
        
        if data.get('frequency') == 'WEEKLY' and data.get('planned_weekday') is None:
            raise serializers.ValidationError({
                'planned_weekday': "Haftalik reja uchun hafta kuni kerak"
            })
        
        return data


class VisitStatisticsSerializer(serializers.Serializer):
    """Serializer for visit statistics"""
    total_visits = serializers.IntegerField()
    completed_visits = serializers.IntegerField()
    in_progress_visits = serializers.IntegerField()
    cancelled_visits = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    average_duration = serializers.FloatField()
    total_images = serializers.IntegerField()
