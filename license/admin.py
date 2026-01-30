from django.contrib import admin
from .models import AppLicense, AppVersionMetadata, AccessHistory

@admin.register(AppLicense)
class AppLicenseAdmin(admin.ModelAdmin):
    list_display = ('license_key', 'entity_type', 'entity_id', 'status', 'starts_at', 'expires_at', 'is_unlimited')
    list_filter = ('entity_type', 'status', 'is_unlimited')
    search_fields = ('license_key', 'entity_id')
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(AppVersionMetadata)
class AppVersionMetadataAdmin(admin.ModelAdmin):
    list_display = ('version_code', 'is_mandatory_update', 'release_date')
    list_filter = ('is_mandatory_update',)
    search_fields = ('version_code',)

@admin.register(AccessHistory)
class AccessHistoryAdmin(admin.ModelAdmin):
    list_display = ('license', 'version', 'ip_address', 'accessed_at')
    list_filter = ('version', 'accessed_at')
    search_fields = ('license__license_key', 'version', 'ip_address')
    readonly_fields = ('accessed_at',)
