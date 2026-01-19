"""
Visit Management Serializers
High-performance serializers with optimized queries
"""
from rest_framework import serializers
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


class VisitListSerializer(serializers.ModelSerializer):
    """Optimized serializer for list views"""
    image_count = serializers.SerializerMethodField()
    is_overdue = serializers.BooleanField(read_only=True)
    agent_details = UserProfileTinySerializer(source='agent', read_only=True)
    client_details = ClientTinySerializer(source='client', read_only=True)
    
    class Meta:
        model = Visit
        fields = [
            'visit_id', 'agent', 'agent_details', 'agent_code', 'agent_name', 
            'client', 'client_details', 'client_code', 'client_name', 
            'visit_type', 'visit_status', 'priority',
            'planned_date', 'planned_time', 'actual_start_time',
            'actual_end_time', 'duration_minutes', 'image_count',
            'is_overdue', 'created_at'
        ]
        read_only_fields = ['visit_id', 'duration_minutes', 'created_at']
    
    def get_image_count(self, obj):
        """Get number of images for this visit"""
        return obj.images.filter(is_deleted=False).count()


class VisitDetailSerializer(serializers.ModelSerializer):
    """Full serializer with all details and nested images"""
    images = VisitImageSerializer(many=True, read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    is_in_progress = serializers.BooleanField(read_only=True)
    agent_details = UserProfileTinySerializer(source='agent', read_only=True)
    client_details = ClientTinySerializer(source='client', read_only=True)
    
    class Meta:
        model = Visit
        fields = '__all__'
        read_only_fields = [
            'visit_id', 'duration_minutes', 'created_at', 'updated_at',
            'cancelled_at'
        ]


class VisitCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new visits"""
    
    class Meta:
        model = Visit
        fields = [
            'agent_code', 'agent_name', 'agent_phone',
            'client_code', 'client_name', 'client_address',
            'visit_type', 'priority', 'planned_date', 'planned_time',
            'planned_duration_minutes', 'purpose', 'tasks_planned'
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
