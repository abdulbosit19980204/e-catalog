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
        fields = [
            'id', 'nomenklatura', 'image', 'is_main', 'category', 'note',
            'status', 'source', 'created_at', 'updated_at', 'is_active', 'is_deleted',
            'image_url', 'image_sm_url', 'image_md_url', 'image_lg_url', 'image_thumbnail_url'
        ]
    
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
        fields = [
            'id', 'code_1c', 'name', 'title', 'description', 'images', 'projects',
            'is_active', 'is_deleted', 'created_at', 'updated_at'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optimizatsiya: Nomenklatura ichida faqat yengil project ma'lumotlarini qaytarish
        self.fields['projects'] = ProjectSimpleSerializer(many=True, read_only=True)
        if 'request' in self.context:
            self.fields['images'].context['request'] = self.context['request']
            self.fields['projects'].context['request'] = self.context['request']

class ProjectImageSerializer(serializers.ModelSerializer):
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


class ThumbnailEntrySerializer(serializers.Serializer):
    """Serializes unified thumbnail feed entries"""

    entity_type = serializers.CharField(help_text="Entity turi (project | client | nomenklatura)")
    entity_id = serializers.IntegerField(help_text="Entity primary key ID si")
    code_1c = serializers.CharField(help_text="Entity ning 1C kodi (code_1c yoki client_code_1c)")
    entity_name = serializers.CharField(help_text="Entity nomi")
    image_id = serializers.IntegerField(help_text="Image primary key ID si")
    thumbnail_url = serializers.URLField(allow_null=True, help_text="Thumbnail rasm URL i")
    thumbnail_dimensions = serializers.DictField(allow_null=True, help_text="Thumbnail rasm o'lchamlari va hajmi (width, height, format, size)")
    original_dimensions = serializers.DictField(allow_null=True, help_text="Original rasm o'lchamlari va hajmi (width, height, format, size_bytes, size)")
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

class ProjectSimpleSerializer(serializers.ModelSerializer):
    """Faqatgina ID, code_1c va name ni qaytaruvchi yengil serializer"""
    is_integration = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'code_1c', 'name', 'is_integration']

    def get_is_integration(self, obj) -> bool:
        return obj.integrations.exists()


class ProjectSerializer(serializers.ModelSerializer):
    images = ProjectImageSerializer(many=True, read_only=True)
    is_integration = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'code_1c', 'name', 'title', 'description', 'is_active', 'is_deleted',
            'created_at', 'updated_at', 'images', 'is_integration'
        ]
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

    def get_is_integration(self, obj) -> bool:
        return obj.integrations.exists()


class ProjectDetailSerializer(ProjectSerializer):
    nomenclatures = APINomenklaturaSerializer(many=True, read_only=True)
    
    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ['nomenclatures']


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

