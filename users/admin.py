from django.contrib import admin
from .models import AuthProject, UserProfile

@admin.register(AuthProject)
class AuthProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'project_code', 'wsdl_url', 'is_active', 'created_at']
    search_fields = ['name', 'project_code']
    list_filter = ['is_active']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'code_1c', 'code_project', 'code_sklad', 'type_1c']
    search_fields = ['user__username', 'code_1c', 'user__first_name']
    raw_id_fields = ['user']
