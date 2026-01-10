from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import Integration, IntegrationLog
import uuid
import threading
from integration.views import sync_nomenklatura_async, sync_clients_async


@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    """Integration admin"""
    list_display = ['name', 'project', 'wsdl_url_short', 'chunk_size', 'is_active', 'is_deleted', 'created_at', 'action_buttons']
    list_filter = ['is_active', 'is_deleted', 'project', 'created_at']
    search_fields = ['name', 'project__name', 'wsdl_url']
    readonly_fields = ['created_at', 'updated_at', 'logs_count_display', 'sync_buttons']
    list_per_page = 25
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('name', 'project', 'description')
        }),
        ('1C Web Service sozlamalari', {
            'fields': ('wsdl_url', 'username', 'password', 'method_nomenklatura', 'method_clients', 'chunk_size')
        }),
        ('Status', {
            'fields': ('is_active', 'is_deleted')
        }),
        ('Sync Operatsiyalari', {
            'fields': ('sync_buttons',),
            'classes': ('collapse',)
        }),
        ('Statistika', {
            'fields': ('logs_count_display',),
            'classes': ('collapse',)
        }),
        ('Vaqt', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def wsdl_url_short(self, obj):
        """WSDL URL'ni qisqartirish"""
        if not obj or not hasattr(obj, 'wsdl_url') or not obj.wsdl_url:
            return "-"
        
        if len(obj.wsdl_url) > 50:
            return format_html(
                '<span title="{}">{}...</span>',
                obj.wsdl_url,
                obj.wsdl_url[:50]
            )
        return obj.wsdl_url
    wsdl_url_short.short_description = "WSDL URL"
    
    def logs_count_display(self, obj):
        """Log'lar sonini ko'rsatish"""
        if not obj or not obj.pk:
            return "-"
        
        count = obj.logs.count()
        completed = obj.logs.filter(status='completed').count()
        error = obj.logs.filter(status='error').count()
        if count > 0:
            url = reverse('admin:integration_integrationlog_changelist')
            return format_html(
                '<a href="{}?integration__id__exact={}">Jami: {} ta</a>, Muvaffaqiyatli: {} ta, Xatolar: {} ta',
                url, obj.id, count, completed, error
            )
        return f"Jami: {count} ta, Muvaffaqiyatli: {completed} ta, Xatolar: {error} ta"
    logs_count_display.short_description = "Log'lar soni"
    
    def action_buttons(self, obj):
        """List view'da sync button'lari"""
        if not obj or not obj.pk or not obj.is_active or obj.is_deleted:
            return "-"
        
        nomenklatura_url = reverse('admin:integration_integration_sync_nomenklatura', args=[obj.id])
        clients_url = reverse('admin:integration_integration_sync_clients', args=[obj.id])
        
        return format_html(
            '<a href="{}" class="button" style="background-color: #417690; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; margin-right: 5px; font-size: 11px;">📦 Nomenklatura</a>'
            '<a href="{}" class="button" style="background-color: #417690; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; font-size: 11px;">👥 Clients</a>',
            nomenklatura_url, clients_url
        )
    action_buttons.short_description = "Sync"
    
    def sync_buttons(self, obj):
        """Detail view'da sync button'lari"""
        # Yangi obyekt yaratish holati (obj None yoki pk None)
        if not obj or not obj.pk:
            return format_html(
                '<p style="color: #666; font-style: italic;">Integration yaratib bo\'lgandan keyin sync operatsiyalarini ishlatishingiz mumkin.</p>'
            )
        
        # Obyekt mavjud, lekin faol emas yoki o'chirilgan
        if not obj.is_active or obj.is_deleted:
            return "Integration faol emas yoki o'chirilgan"
        
        nomenklatura_url = reverse('admin:integration_integration_sync_nomenklatura', args=[obj.id])
        clients_url = reverse('admin:integration_integration_sync_clients', args=[obj.id])
        logs_url = reverse('admin:integration_integrationlog_changelist')
        
        return format_html(
            '<div style="margin: 10px 0;">'
            '<a href="{}" class="button" style="background-color: #417690; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-right: 10px; display: inline-block; font-weight: bold;">📦 Nomenklatura Sync</a>'
            '<a href="{}" class="button" style="background-color: #417690; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">👥 Clients Sync</a>'
            '</div>'
            '<div style="margin-top: 15px;">'
            '<a href="{}?integration__id__exact={}" style="color: #417690; text-decoration: underline;">📊 Log\'larni ko\'rish</a>'
            '</div>',
            nomenklatura_url, clients_url, logs_url, obj.id
        )
    sync_buttons.short_description = "Sync Operatsiyalari"
    
    def get_urls(self):
        """Custom URL'lar qo'shish"""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:integration_id>/sync/nomenklatura/',
                self.admin_site.admin_view(self.sync_nomenklatura),
                name='integration_integration_sync_nomenklatura',
            ),
            path(
                '<int:integration_id>/sync/clients/',
                self.admin_site.admin_view(self.sync_clients),
                name='integration_integration_sync_clients',
            ),
        ]
        return custom_urls + urls
    
    def sync_nomenklatura(self, request, integration_id):
        """Nomenklatura sync'ni ishga tushirish"""
        try:
            integration = Integration.objects.get(id=integration_id, is_active=True, is_deleted=False)
            task_id = str(uuid.uuid4())
            
            # Background thread'da ishlash
            thread = threading.Thread(target=sync_nomenklatura_async, args=(task_id, integration.id))
            thread.daemon = True
            thread.start()
            
            log_url = reverse('admin:integration_integrationlog_changelist') + f'?task_id__exact={task_id}'
            messages.success(
                request,
                f'Nomenklatura sync boshlandi. Task ID: {task_id[:8]}... '
                f'<a href="{log_url}" target="_blank">Log\'larni ko\'rish</a>'
            )
        except Integration.DoesNotExist:
            messages.error(request, "Integration topilmadi yoki faol emas")
        except Exception as e:
            messages.error(request, f"Xatolik: {str(e)}")
        
        return HttpResponseRedirect(reverse('admin:integration_integration_change', args=[integration_id]))
    
    def sync_clients(self, request, integration_id):
        """Clients sync'ni ishga tushirish"""
        try:
            integration = Integration.objects.get(id=integration_id, is_active=True, is_deleted=False)
            task_id = str(uuid.uuid4())
            
            # Background thread'da ishlash
            thread = threading.Thread(target=sync_clients_async, args=(task_id, integration.id))
            thread.daemon = True
            thread.start()
            
            log_url = reverse('admin:integration_integrationlog_changelist') + f'?task_id__exact={task_id}'
            messages.success(
                request,
                f'Clients sync boshlandi. Task ID: {task_id[:8]}... '
                f'<a href="{log_url}" target="_blank">Log\'larni ko\'rish</a>'
            )
        except Integration.DoesNotExist:
            messages.error(request, "Integration topilmadi yoki faol emas")
        except Exception as e:
            messages.error(request, f"Xatolik: {str(e)}")
        
        return HttpResponseRedirect(reverse('admin:integration_integration_change', args=[integration_id]))
    
    def get_queryset(self, request):
        """Optimizatsiya: prefetch_related bilan logs yuklash"""
        return super().get_queryset(request).prefetch_related('logs')


@admin.register(IntegrationLog)
class IntegrationLogAdmin(admin.ModelAdmin):
    """IntegrationLog admin"""
    list_display = ['integration', 'sync_type', 'status_badge', 'progress_bar', 'total_items', 'processed_items', 'created_items', 'updated_items', 'error_items', 'start_time']
    list_filter = ['status', 'sync_type', 'integration', 'start_time']
    search_fields = ['integration__name', 'task_id', 'error_details']
    readonly_fields = ['task_id', 'start_time', 'end_time', 'created_at', 'updated_at', 'progress_bar_display']
    list_per_page = 25
    date_hierarchy = 'start_time'
    ordering = ['-start_time']
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('integration', 'task_id', 'sync_type', 'status')
        }),
        ('Progress', {
            'fields': ('total_items', 'processed_items', 'created_items', 'updated_items', 'error_items', 'progress_bar_display')
        }),
        ('Xatolar', {
            'fields': ('error_details',),
            'classes': ('collapse',)
        }),
        ('Vaqt', {
            'fields': ('start_time', 'end_time', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Status badge ko'rsatish"""
        colors = {
            'fetching': '#17a2b8',
            'processing': '#ffc107',
            'completed': '#28a745',
            'error': '#dc3545'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-size: 12px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = "Status"
    
    def progress_bar(self, obj):
        """Progress bar ko'rsatish"""
        if obj.total_items > 0:
            percent = obj.progress_percent
            color = '#28a745' if obj.status == 'completed' else '#007bff'
            return format_html(
                '<div style="width: 100px; background-color: #e9ecef; border-radius: 3px; height: 20px; position: relative;">'
                '<div style="width: {}%; background-color: {}; height: 100%; border-radius: 3px; text-align: center; line-height: 20px; color: white; font-size: 10px;">{}%</div>'
                '</div>',
                percent, color, percent
            )
        return "-"
    progress_bar.short_description = "Progress"
    
    def progress_bar_display(self, obj):
        """Progress bar ko'rsatish (readonly field)"""
        if obj.total_items > 0:
            percent = obj.progress_percent
            color = '#28a745' if obj.status == 'completed' else '#007bff'
            return format_html(
                '<div style="width: 300px; background-color: #e9ecef; border-radius: 5px; height: 30px; position: relative; margin: 10px 0;">'
                '<div style="width: {}%; background-color: {}; height: 100%; border-radius: 5px; text-align: center; line-height: 30px; color: white; font-weight: bold;">{}% ({} / {})</div>'
                '</div>',
                percent, color, percent, obj.processed_items, obj.total_items
            )
        return "-"
    progress_bar_display.short_description = "Progress"
    
    def has_add_permission(self, request):
        return False  # Log'lar faqat avtomatik yaratiladi
    
    def get_queryset(self, request):
        """Optimizatsiya: select_related bilan integration yuklash"""
        return super().get_queryset(request).select_related('integration')
