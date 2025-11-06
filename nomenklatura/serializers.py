from rest_framework import serializers
from .models import Nomenklatura, NomenklaturaImage

class NomenklaturaImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    image_sm_url = serializers.SerializerMethodField()
    image_md_url = serializers.SerializerMethodField()
    image_lg_url = serializers.SerializerMethodField()
    image_thumbnail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = NomenklaturaImage
        fields = ['id', 'nomenklatura', 'image', 'image_url', 'image_sm_url', 'image_md_url', 'image_lg_url', 'image_thumbnail_url', 'is_main', 'created_at']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'image': {'required': False}
        }
    
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

