from typing import Optional, Dict
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from PIL import Image
from nomenklatura.models import Nomenklatura, NomenklaturaImage
from .models import Project, ProjectImage, ImageStatus, ImageSource, AgentLocation


class ImageStatusSerializer(serializers.ModelSerializer):
    """ImageStatus serializer"""
    class Meta:
        model = ImageStatus
        fields = ['id', 'code', 'name', 'description', 'icon', 'order', 'is_active']
        read_only_fields = ['id']


class ImageSourceSerializer(serializers.ModelSerializer):
    """ImageSource serializer"""
    uploader_type_display = serializers.CharField(source='get_uploader_type_display', read_only=True)
    
    class Meta:
        model = ImageSource
        fields = [
            'id', 'uploader_name', 'uploader_type', 'uploader_type_display',
            'uploader_contact', 'upload_location', 'upload_device', 'notes',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class APINomenklaturaImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    image_sm_url = serializers.SerializerMethodField()
    image_md_url = serializers.SerializerMethodField()
    image_lg_url = serializers.SerializerMethodField()
    image_thumbnail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = NomenklaturaImage
        fields = '__all__'
    
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

class APINomenklaturaSerializer(serializers.ModelSerializer):
    images = APINomenklaturaImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Nomenklatura
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pass request context to nested serializer
        if 'request' in self.context:
            self.fields['images'].context['request'] = self.context['request']

class ProjectImageSerializer(serializers.ModelSerializer):
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
        model = ProjectImage
        fields = [
            'id',
            'project',
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
    
    @extend_schema_field(OpenApiTypes.URI)
    def get_image_url(self, obj) -> Optional[str]:
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    @extend_schema_field(OpenApiTypes.URI)
    def get_image_sm_url(self, obj) -> Optional[str]:
        if obj.image_sm:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_sm.url)
            return obj.image_sm.url
        return None
    
    @extend_schema_field(OpenApiTypes.URI)
    def get_image_md_url(self, obj) -> Optional[str]:
        if obj.image_md:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_md.url)
            return obj.image_md.url
        return None
    
    @extend_schema_field(OpenApiTypes.URI)
    def get_image_lg_url(self, obj) -> Optional[str]:
        if obj.image_lg:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_lg.url)
            return obj.image_lg.url
        return None
    
    @extend_schema_field(OpenApiTypes.URI)
    def get_image_thumbnail_url(self, obj) -> Optional[str]:
        if obj.image_thumbnail:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_thumbnail.url)
            return obj.image_thumbnail.url
        return None
    
    def _get_image_dimensions(self, image_field) -> Optional[Dict[str, any]]:
        """Rasm o'lchamlarini va hajmini olish"""
        if not image_field:
            return None
        try:
            if hasattr(image_field, 'file') and image_field.file:
                with Image.open(image_field.file) as img:
                    # Fayl hajmini olish
                    file_size = 0
                    if hasattr(image_field.file, 'size'):
                        file_size = image_field.file.size
                    elif hasattr(image_field, 'size'):
                        file_size = image_field.size
                    
                    # KB yoki MB ga aylantirish
                    if file_size >= 1024 * 1024:  # MB
                        size_str = f"{file_size / (1024 * 1024):.2f} MB"
                    elif file_size >= 1024:  # KB
                        size_str = f"{file_size / 1024:.2f} KB"
                    else:  # Bytes
                        size_str = f"{file_size} B"
                    
                    return {
                        'width': img.width,
                        'height': img.height,
                        'format': img.format or 'JPEG',
                        'size_bytes': file_size,
                        'size': size_str
                    }
        except Exception:
            pass
        return None
    
    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_image_dimensions(self, obj) -> Optional[Dict[str, int]]:
        """Original rasm o'lchamlari"""
        return self._get_image_dimensions(obj.image)
    
    def _get_cached_image_size(self, image_field) -> Optional[str]:
        """Cache qilingan rasm hajmini olish"""
        if not image_field:
            return None
        try:
            if hasattr(image_field, 'file') and image_field.file:
                file_size = image_field.file.size
                if file_size >= 1024 * 1024:  # MB
                    return f"{file_size / (1024 * 1024):.2f} MB"
                elif file_size >= 1024:  # KB
                    return f"{file_size / 1024:.2f} KB"
                else:  # Bytes
                    return f"{file_size} B"
        except Exception:
            pass
        return None
    
    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_image_sm_dimensions(self, obj) -> Optional[Dict[str, any]]:
        """Kichik rasm o'lchamlari (300x300)"""
        if obj.image_sm:
            size_str = self._get_cached_image_size(obj.image_sm)
            return {
                'width': 300,
                'height': 300,
                'format': 'JPEG',
                'size': size_str
            }
        return None
    
    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_image_md_dimensions(self, obj) -> Optional[Dict[str, any]]:
        """O'rta rasm o'lchamlari (600x600)"""
        if obj.image_md:
            size_str = self._get_cached_image_size(obj.image_md)
            return {
                'width': 600,
                'height': 600,
                'format': 'JPEG',
                'size': size_str
            }
        return None
    
    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_image_lg_dimensions(self, obj) -> Optional[Dict[str, any]]:
        """Katta rasm o'lchamlari (1200x1200)"""
        if obj.image_lg:
            size_str = self._get_cached_image_size(obj.image_lg)
            return {
                'width': 1200,
                'height': 1200,
                'format': 'JPEG',
                'size': size_str
            }
        return None
    
    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_image_thumbnail_dimensions(self, obj) -> Optional[Dict[str, any]]:
        """Thumbnail rasm o'lchamlari (150x150)"""
        if obj.image_thumbnail:
            size_str = self._get_cached_image_size(obj.image_thumbnail)
            return {
                'width': 150,
                'height': 150,
                'format': 'JPEG',
                'size': size_str
            }
        return None


class ThumbnailEntrySerializer(serializers.Serializer):
    """Serializes unified thumbnail feed entries"""

    entity_type = serializers.CharField(help_text="Entity turi (project | client | nomenklatura)")
    entity_id = serializers.IntegerField(help_text="Entity primary key ID si")
    code_1c = serializers.CharField(help_text="Entity ning 1C kodi (code_1c yoki client_code_1c)")
    entity_name = serializers.CharField(help_text="Entity nomi")
    image_id = serializers.IntegerField(help_text="Image primary key ID si")
    thumbnail_url = serializers.URLField(allow_null=True, help_text="Thumbnail rasm URL i")
    is_main = serializers.BooleanField(help_text="Asosiy rasm statusi")
    category = serializers.CharField(allow_null=True, help_text="Rasm toifasi", default=None)
    note = serializers.CharField(allow_null=True, help_text="Rasm izohi", default=None)
    status_code = serializers.CharField(allow_null=True, help_text="Image status kodi", default=None)
    status_name = serializers.CharField(allow_null=True, help_text="Image status nomi", default=None)
    source_name = serializers.CharField(allow_null=True, help_text="Rasmni yuboruvchi nomi", default=None)
    source_type = serializers.CharField(allow_null=True, help_text="Rasmni yuboruvchi turi", default=None)
    created_at = serializers.DateTimeField(help_text="Rasm yaratilingan vaqti")


class AgentLocationSerializer(serializers.ModelSerializer):
    """AgentLocation serializer - barcha maydonlar ixtiyoriy"""
    class Meta:
        model = AgentLocation
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class ProjectSerializer(serializers.ModelSerializer):
    images = ProjectImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
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


class ProjectImageBulkUploadSerializer(serializers.Serializer):
    """Bir project uchun bir nechta rasm yuklash uchun schema."""

    project = serializers.CharField(
        help_text="Rasm bog'lanadigan project'ning `code_1c` qiymati", max_length=255
    )
    images = serializers.ListField(
        child=serializers.ImageField(),
        allow_empty=False,
        help_text="Multipart form-data da yuboriladigan bir yoki bir nechta rasm fayllari",
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

