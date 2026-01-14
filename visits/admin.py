from django.contrib import admin
from .models import Visit, VisitPlan, VisitImage


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = [
        'visit_id', 'agent_name', 'client_name', 'planned_date',
        'visit_type', 'visit_status', 'priority', 'duration_minutes'
    ]
    list_filter = [
        'visit_status', 'visit_type', 'priority', 'planned_date',
        'created_at', 'is_deleted'
    ]
    search_fields = [
        'agent_code', 'agent_name', 'client_code', 'client_name',
        'purpose', 'notes'
    ]
    readonly_fields = [
        'visit_id', 'created_at', 'updated_at', 'duration_minutes',
        'cancelled_at'
    ]
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('visit_id', 'visit_type', 'visit_status', 'priority')
        }),
        ('Agent', {
            'fields': ('agent_code', 'agent_name', 'agent_phone')
        }),
        ('Klient', {
            'fields': ('client_code', 'client_name', 'client_address')
        }),
        ('Rejalashtirish', {
            'fields': (
                'planned_date', 'planned_time', 'planned_duration_minutes',
                'purpose', 'tasks_planned'
            )
        }),
        ('Haqiqiy vaqt', {
            'fields': (
                'actual_start_time', 'actual_end_time', 'duration_minutes'
            )
        }),
        ('Joylashuv', {
            'fields': (
                'check_in_latitude', 'check_in_longitude', 'check_in_address',
                'check_in_accuracy', 'check_out_latitude', 'check_out_longitude'
            )
        }),
        ('Natijalar', {
            'fields': (
                'tasks_completed', 'outcome', 'notes',
                'next_visit_date', 'next_visit_notes'
            )
        }),
        ('Baholash', {
            'fields': (
                'client_satisfaction', 'agent_notes', 'supervisor_notes'
            )
        }),
        ('Bekor qilish', {
            'fields': ('cancelled_reason', 'cancelled_by', 'cancelled_at'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'is_deleted'),
            'classes': ('collapse',)
        }),
    )
    date_hierarchy = 'planned_date'
    ordering = ['-planned_date', '-planned_time']


@admin.register(VisitPlan)
class VisitPlanAdmin(admin.ModelAdmin):
    list_display = [
        'plan_id', 'agent_code', 'client_code', 'frequency',
        'planned_weekday', 'planned_time', 'is_active'
    ]
    list_filter = ['frequency', 'is_active', 'priority', 'auto_generate']
    search_fields = ['agent_code', 'client_code']
    readonly_fields = ['plan_id', 'created_at', 'updated_at']
    fieldsets = (
        ('Asosiy', {
            'fields': ('plan_id', 'agent_code', 'client_code')
        }),
        ('Jadval', {
            'fields': (
                'frequency', 'planned_weekday', 'planned_time',
                'duration_minutes', 'start_date', 'end_date'
            )
        }),
        ('Sozlamalar', {
            'fields': (
                'is_active', 'priority', 'auto_generate',
                'generate_days_ahead'
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'is_deleted'),
            'classes': ('collapse',)
        }),
    )
    ordering = ['agent_code', 'planned_weekday', 'planned_time']


@admin.register(VisitImage)
class VisitImageAdmin(admin.ModelAdmin):
    list_display = [
        'image_id', 'visit', 'image_type', 'captured_at',
        'latitude', 'longitude'
    ]
    list_filter = ['image_type', 'captured_at', 'is_deleted']
    search_fields = ['visit__visit_id', 'notes']
    readonly_fields = ['image_id', 'captured_at', 'created_at', 'updated_at']
    fieldsets = (
        ('Asosiy', {
            'fields': ('image_id', 'visit', 'image_type')
        }),
        ('Rasm', {
            'fields': ('image_url', 'thumbnail_url')
        }),
        ('Joylashuv', {
            'fields': ('latitude', 'longitude', 'captured_at')
        }),
        ('Bog\'lanish', {
            'fields': ('client_image_id', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'is_deleted'),
            'classes': ('collapse',)
        }),
    )
    date_hierarchy = 'captured_at'
    ordering = ['-captured_at']
