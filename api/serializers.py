from rest_framework import serializers
from nomenklatura.models import Nomenklatura, NomenklaturaImage
from .models import Project, ProjectImage

class APINomenklaturaImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    image_sm_url = serializers.SerializerMethodField()
    image_md_url = serializers.SerializerMethodField()
    image_lg_url = serializers.SerializerMethodField()
    image_thumbnail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = NomenklaturaImage
        fields = '__all__'
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def get_image_sm_url(self, obj):
        if obj.image_sm:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_sm.url)
            return obj.image_sm.url
        return None
    
    def get_image_md_url(self, obj):
        if obj.image_md:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_md.url)
            return obj.image_md.url
        return None
    
    def get_image_lg_url(self, obj):
        if obj.image_lg:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_lg.url)
            return obj.image_lg.url
        return None
    
    def get_image_thumbnail_url(self, obj):
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
    
    class Meta:
        model = ProjectImage
        fields = ['id', 'project', 'image', 'image_url', 'image_sm_url', 'image_md_url', 'image_lg_url', 'image_thumbnail_url', 'is_main', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def get_image_sm_url(self, obj):
        if obj.image_sm:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_sm.url)
            return obj.image_sm.url
        return None
    
    def get_image_md_url(self, obj):
        if obj.image_md:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_md.url)
            return obj.image_md.url
        return None
    
    def get_image_lg_url(self, obj):
        if obj.image_lg:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_lg.url)
            return obj.image_lg.url
        return None
    
    def get_image_thumbnail_url(self, obj):
        if obj.image_thumbnail:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_thumbnail.url)
            return obj.image_thumbnail.url
        return None

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

