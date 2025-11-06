from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Client, ClientImage


class ClientImageInline(admin.TabularInline):
    """ClientImage inline admin"""
    model = ClientImage
    extra = 1
    fields = ('image', 'image_preview', 'is_main', 'is_active')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        """Rasm ko'rinishini ko'rsatish"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px;" />',
                obj.image.url
            )
        return "Rasm yo'q"
    image_preview.short_description = "Rasm"


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Client admin"""
    list_display = ['name', 'client_code_1c', 'email', 'phone', 'images_count', 'is_active', 'is_deleted', 'created_at']
    list_filter = ['is_active', 'is_deleted', 'created_at', 'updated_at']
    search_fields = ['name', 'client_code_1c', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'images_count_display']
    inlines = [ClientImageInline]
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('client_code_1c', 'name', 'email', 'phone', 'description')
        }),
        ('Status', {
            'fields': ('is_active', 'is_deleted')
        }),
        ('Statistika', {
            'fields': ('images_count_display',),
            'classes': ('collapse',)
        }),
        ('Vaqt', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    list_per_page = 25
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def images_count(self, obj):
        """Rasmlar sonini ko'rsatish"""
        count = obj.images.filter(is_deleted=False).count()
        if count > 0:
            url = reverse('admin:client_clientimage_changelist')
            return format_html(
                '<a href="{}?client__id__exact={}">{} ta</a>',
                url, obj.id, count
            )
        return "0 ta"
    images_count.short_description = "Rasmlar"
    
    def images_count_display(self, obj):
        """Rasmlar sonini ko'rsatish (readonly field)"""
        count = obj.images.filter(is_deleted=False).count()
        main_count = obj.images.filter(is_deleted=False, is_main=True).count()
        return f"Jami: {count} ta, Asosiy: {main_count} ta"
    images_count_display.short_description = "Rasmlar soni"
    
    def get_queryset(self, request):
        """Optimizatsiya: prefetch_related bilan images yuklash"""
        return super().get_queryset(request).prefetch_related('images')


@admin.register(ClientImage)
class ClientImageAdmin(admin.ModelAdmin):
    """ClientImage admin"""
    list_display = ['image_preview', 'client', 'is_main', 'is_active', 'is_deleted', 'created_at']
    list_filter = ['is_main', 'is_active', 'is_deleted', 'client', 'created_at']
    search_fields = ['client__name', 'client__client_code_1c']
    readonly_fields = ['image_preview', 'created_at', 'updated_at']
    list_per_page = 25
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('client', 'image', 'image_preview', 'is_main')
        }),
        ('Status', {
            'fields': ('is_active', 'is_deleted')
        }),
        ('Vaqt', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        """Rasm ko'rinishini ko'rsatish"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px;" />',
                obj.image.url
            )
        return "Rasm yo'q"
    image_preview.short_description = "Rasm"
    
    def get_queryset(self, request):
        """Optimizatsiya: select_related bilan client yuklash"""
        return super().get_queryset(request).select_related('client')
