from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import UserProfile, AgentBusinessRegion

User = get_user_model()

class AgentBusinessRegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentBusinessRegion
        fields = ['code', 'name']

class UserProfileSerializer(serializers.ModelSerializer):
    business_regions = AgentBusinessRegionSerializer(many=True, read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['code_1c', 'code_project', 'code_sklad', 'type_1c', 'business_region_code', 'business_region_name', 'business_regions']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(source='userprofile', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'profile']
        read_only_fields = ['id']
