from rest_framework import serializers
from .models import AppLicense, AppVersionMetadata, AccessHistory

class AppLicenseSerializer(serializers.ModelSerializer):
    days_remaining = serializers.SerializerMethodField()

    class Meta:
        model = AppLicense
        fields = ('license_key', 'status', 'starts_at', 'expires_at', 'is_unlimited', 'days_remaining')

    def get_days_remaining(self, obj):
        if obj.is_unlimited:
            return 9999
        if obj.expires_at:
            from django.utils import timezone
            delta = obj.expires_at - timezone.now()
            return max(0, delta.days)
        return 0

class AppVersionMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppVersionMetadata
        fields = '__all__'

class AccessHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessHistory
        fields = '__all__'
