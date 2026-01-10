from typing import Optional, Dict
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from PIL import Image
from api.serializers import ImageStatusSerializer, ImageSourceSerializer, ProjectSerializer, ProjectSimpleSerializer
from api.models import ImageStatus, ImageSource, Project
from .models import Client, ClientImage

class ClientImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    image_sm_url = serializers.SerializerMethodField()
    image_md_url = serializers.SerializerMethodField()
    image_lg_url = serializers.SerializerMethodField()
    image_thumbnail_url = serializers.SerializerMethodField()
    status = ImageStatusSerializer(read_only=True)
    status_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    source = ImageSourceSerializer(read_only=True)
    source_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = ClientImage
        fields = [
            'id',
            'client',
            'image',
            'category',
            'note',
            'image_url',
            'image_sm_url',
            'image_md_url',
            'image_lg_url',
            'image_thumbnail_url',
            'is_main',
            'status',
            'status_id',
            'source',
            'source_id',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
    
    def create(self, validated_data):
        """Create qilganda status_id va source_id ni to'g'ri ishlatish"""
        status_id = validated_data.pop('status_id', None)
        source_id = validated_data.pop('source_id', None)
        
        instance = super().create(validated_data)
        
        if status_id:
            try:
                instance.status = ImageStatus.objects.get(id=status_id, is_deleted=False)
            except ImageStatus.DoesNotExist:
                pass
        
        if source_id:
            try:
                instance.source = ImageSource.objects.get(id=source_id, is_deleted=False)
            except ImageSource.DoesNotExist:
                pass
        
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        """Update qilganda status_id va source_id ni to'g'ri ishlatish"""
        status_id = validated_data.pop('status_id', None)
        source_id = validated_data.pop('source_id', None)
        
        instance = super().update(instance, validated_data)
        
        if status_id is not None:
            if status_id:
                try:
                    instance.status = ImageStatus.objects.get(id=status_id, is_deleted=False)
                except ImageStatus.DoesNotExist:
                    instance.status = None
            else:
                instance.status = None
        
        if source_id is not None:
            if source_id:
                try:
                    instance.source = ImageSource.objects.get(id=source_id, is_deleted=False)
                except ImageSource.DoesNotExist:
                    instance.source = None
            else:
                instance.source = None
        
        instance.save()
        return instance
    
    def get_image_url(self, obj) -> Optional[str]:
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def get_image_sm_url(self, obj) -> Optional[str]:
        if obj.image_sm:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_sm.url)
            return obj.image_sm.url
        return None
    
    def get_image_md_url(self, obj) -> Optional[str]:
        if obj.image_md:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_md.url)
            return obj.image_md.url
        return None
    
    def get_image_lg_url(self, obj) -> Optional[str]:
        if obj.image_lg:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_lg.url)
            return obj.image_lg.url
        return None
    
    def get_image_thumbnail_url(self, obj) -> Optional[str]:
        if obj.image_thumbnail:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_thumbnail.url)
            return obj.image_thumbnail.url
        return None
    
    def get_image_thumbnail_url(self, obj) -> Optional[str]:
        if obj.image_thumbnail:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_thumbnail.url)
            return obj.image_thumbnail.url
        return None

class ClientSerializer(serializers.ModelSerializer):
    images = ClientImageSerializer(many=True, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)
    project_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="Project ID lari ro'yxati"
    )
    
    class Meta:
        model = Client
        fields = [
            'id', 'projects', 'project_ids', 'client_code_1c', 'name', 'email', 'phone', 'description', 
            'company_name', 'tax_id', 'registration_number', 'legal_address',
            'actual_address', 'fax', 'website', 'social_media', 'additional_phones',
            'industry', 'business_type', 'employee_count', 'annual_revenue',
            'established_date', 'payment_terms', 'credit_limit', 'currency',
            'city', 'region', 'country', 'postal_code', 'contact_person',
            'contact_position', 'contact_email', 'contact_phone', 'notes',
            'tags', 'rating', 'priority', 'source', 'metadata',
            'is_active', 'is_deleted', 'created_at', 'updated_at', 'images'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'client_code_1c': {'required': False}  # Update qilganda required emas
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optimizatsiya: Client ichida faqat yengil project ma'lumotlarini qaytarish
        self.fields['projects'] = ProjectSimpleSerializer(many=True, read_only=True)
        # Pass request context to nested serializer
        if 'request' in self.context:
            self.fields['images'].context['request'] = self.context['request']
            self.fields['projects'].context['request'] = self.context['request']
    
    def create(self, validated_data):
        project_ids = validated_data.pop('project_ids', None)
        instance = super().create(validated_data)
        if project_ids is not None:
            instance.projects.set(Project.objects.filter(id__in=project_ids))
        return instance

    def update(self, instance, validated_data):
        """Update qilganda client_code_1c o'zgartirilmasligi kerak"""
        validated_data.pop('client_code_1c', None)  # client_code_1c o'zgartirilmaydi
        project_ids = validated_data.pop('project_ids', None)
        
        instance = super().update(instance, validated_data)
        
        if project_ids is not None:
            instance.projects.set(Project.objects.filter(id__in=project_ids))
            
        return instance


class ClientImageBulkUploadSerializer(serializers.Serializer):
    """Client image bulk upload uchun schema."""

    client = serializers.CharField(
        help_text="Rasm bog'lanadigan client'ning `client_code_1c` qiymati", max_length=255
    )
    images = serializers.ListField(
        child=serializers.ImageField(),
        allow_empty=False,
        help_text="Multipart form-data formatidagi bir yoki bir nechta rasm fayllari",
    )
    category = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Optional: barcha rasmlar uchun umumiy toifa nomi",
        max_length=120,
    )
    note = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Optional: barcha rasmlar uchun umumiy izoh",
        max_length=255,
    )

