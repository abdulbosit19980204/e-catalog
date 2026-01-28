from django.contrib import admin
from .models import SystemSettings

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ('key', 'value_display', 'is_secret', 'is_active', 'updated_at')
    list_filter = ('is_active', 'is_secret')
    search_fields = ('key', 'description')
    
    def value_display(self, obj):
        if obj.is_secret:
            return "********"
        return obj.value
    value_display.short_description = "Value"
