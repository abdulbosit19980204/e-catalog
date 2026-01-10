from typing import Optional, Dict
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from PIL import Image
from api.serializers import ImageStatusSerializer, ImageSourceSerializer, ProjectSerializer, ProjectSimpleSerializer
from api.models import ImageStatus, ImageSource, Project
from .models import Nomenklatura, NomenklaturaImage

class NomenklaturaImageSerializer(serializers.ModelSerializer):
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
        model = NomenklaturaImage
        fields = [
            'id',
            'nomenklatura',
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
        extra_kwargs = {
            'image': {'required': False}
        }
    
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

class NomenklaturaSerializer(serializers.ModelSerializer):
    images = NomenklaturaImageSerializer(many=True, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)
    project_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="Project ID lari ro'yxati"
    )
    
    class Meta:
        model = Nomenklatura
        fields = [
            'id', 'projects', 'project_ids', 'code_1c', 'name', 'title', 'description',
            'sku', 'barcode', 'brand', 'manufacturer', 'model', 'series', 'vendor_code',
            'base_price', 'sale_price', 'cost_price', 'currency', 'discount_percent',
            'tax_rate', 'stock_quantity', 'min_stock', 'max_stock', 'unit_of_measure',
            'weight', 'dimensions', 'volume', 'category', 'subcategory', 'tags',
            'color', 'size', 'material', 'warranty_period', 'expiry_date',
            'production_date', 'notes', 'rating', 'popularity_score', 'seo_keywords',
            'source', 'metadata', 'is_active', 'is_deleted', 'created_at', 'updated_at',
            'images',
        ]
        extra_kwargs = {
            'code_1c': {'required': False}  # Update qilganda required emas
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optimizatsiya: Nomenklatura ichida faqat yengil project ma'lumotlarini qaytarish
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
        """Update qilganda code_1c o'zgartirilmasligi kerak"""
        validated_data.pop('code_1c', None)  # code_1c o'zgartirilmaydi
        project_ids = validated_data.pop('project_ids', None)
        
        instance = super().update(instance, validated_data)
        
        if project_ids is not None:
            instance.projects.set(Project.objects.filter(id__in=project_ids))
            
        return instance


class NomenklaturaImageBulkUploadSerializer(serializers.Serializer):
    """Nomenklatura image bulk upload uchun schema."""

    nomenklatura = serializers.CharField(
        help_text="Rasm bog'lanadigan nomenklatura'ning `code_1c` qiymati", max_length=255
    )
    images = serializers.ListField(
        child=serializers.ImageField(),
        allow_empty=False,
        help_text="Multipart form-data ko'rinishidagi bir yoki bir nechta rasm fayllari",
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

