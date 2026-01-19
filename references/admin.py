from django.contrib import admin
from .models import VisitType, VisitStatus, VisitPriority, VisitStep

@admin.register(VisitType)
class VisitTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'sort_order', 'created_at']
    search_fields = ['code', 'name']
    ordering = ['sort_order', 'name']

@admin.register(VisitStatus)
class VisitStatusAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'color', 'is_final', 'sort_order']
    list_filter = ['is_final']
    search_fields = ['code', 'name']
    ordering = ['sort_order', 'name']

@admin.register(VisitPriority)
class VisitPriorityAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'level', 'color']
    search_fields = ['code', 'name']
    ordering = ['-level', 'name']

@admin.register(VisitStep)
class VisitStepAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'input_type', 'is_required', 'sort_order']
    list_filter = ['project', 'input_type', 'is_required']
    search_fields = ['title', 'description']
    ordering = ['project', 'sort_order']
