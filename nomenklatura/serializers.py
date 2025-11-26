from typing import Optional, Dict
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from PIL import Image
from api.serializers import ImageStatusSerializer, ImageSourceSerializer
from api.models import ImageStatus, ImageSource
from .models import Nomenklatura, NomenklaturaImage

class NomenklaturaImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    image_sm_url = serializers.SerializerMethodField()
    image_md_url = serializers.SerializerMethodField()
    image_lg_url = serializers.SerializerMethodField()
    image_thumbnail_url = serializers.SerializerMethodField()
    image_dimensions = serializers.SerializerMethodField()
    image_sm_dimensions = serializers.SerializerMethodField()
    image_md_dimensions = serializers.SerializerMethodField()
    image_lg_dimensions = serializers.SerializerMethodField()
    image_thumbnail_dimensions = serializers.SerializerMethodField()
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
            'image_dimensions',
            'image_sm_dimensions',
            'image_md_dimensions',
            'image_lg_dimensions',
            'image_thumbnail_dimensions',
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
    
    def _get_image_dimensions(self, image_field) -> Optional[Dict[str, int]]:
        """Rasm o'lchamlarini olish"""
        if not image_field:
            return None
        try:
            if hasattr(image_field, 'file') and image_field.file:
                with Image.open(image_field.file) as img:
                    return {
                        'width': img.width,
                        'height': img.height,
                        'format': img.format or 'JPEG'
                    }
        except Exception:
            pass
        return None
    
    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_image_dimensions(self, obj) -> Optional[Dict[str, int]]:
        """Original rasm o'lchamlari"""
        return self._get_image_dimensions(obj.image)
    
    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_image_sm_dimensions(self, obj) -> Optional[Dict[str, int]]:
        """Kichik rasm o'lchamlari (300x300)"""
        if obj.image_sm:
            return {'width': 300, 'height': 300, 'format': 'JPEG'}
        return None
    
    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_image_md_dimensions(self, obj) -> Optional[Dict[str, int]]:
        """O'rta rasm o'lchamlari (600x600)"""
        if obj.image_md:
            return {'width': 600, 'height': 600, 'format': 'JPEG'}
        return None
    
    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_image_lg_dimensions(self, obj) -> Optional[Dict[str, int]]:
        """Katta rasm o'lchamlari (1200x1200)"""
        if obj.image_lg:
            return {'width': 1200, 'height': 1200, 'format': 'JPEG'}
        return None
    
    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_image_thumbnail_dimensions(self, obj) -> Optional[Dict[str, int]]:
        """Thumbnail rasm o'lchamlari (150x150)"""
        if obj.image_thumbnail:
            return {'width': 150, 'height': 150, 'format': 'JPEG'}
        return None

class NomenklaturaSerializer(serializers.ModelSerializer):
    images = NomenklaturaImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Nomenklatura
        fields = '__all__'
        extra_kwargs = {
            'code_1c': {'required': False}  # Update qilganda required emas
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pass request context to nested serializer
        if 'request' in self.context:
            self.fields['images'].context['request'] = self.context['request']
    
    def update(self, instance, validated_data):
        """Update qilganda code_1c o'zgartirilmasligi kerak"""
        validated_data.pop('code_1c', None)  # code_1c o'zgartirilmaydi
        return super().update(instance, validated_data)


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

