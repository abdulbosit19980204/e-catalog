from django.contrib import admin
from django.db.models import Q
from django.utils.html import format_html
from django.urls import reverse
from .models import Project, ProjectImage, ImageStatus, ImageSource


class ProjectImageInline(admin.TabularInline):
    """ProjectImage inline admin"""
    model = ProjectImage
    extra = 1
    fields = ('image', 'image_preview', 'is_main', 'category', 'note', 'status', 'source', 'is_active')
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


class DescriptionStatusFilter(admin.SimpleListFilter):
    title = "Description holati"
    parameter_name = "description_status"

    def lookups(self, request, model_admin):
        return (
            ("with", "Description bor"),
            ("without", "Description yo'q"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == "with":
            return queryset.exclude(Q(description__isnull=True) | Q(description__exact=""))
        if value == "without":
            return queryset.filter(Q(description__isnull=True) | Q(description__exact=""))
        return queryset


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Project admin"""
    list_display = ['name', 'code_1c', 'title', 'images_count', 'is_active', 'is_deleted', 'created_at']
    list_filter = ['is_active', 'is_deleted', DescriptionStatusFilter, 'created_at', 'updated_at']
    search_fields = ['name', 'code_1c', 'title']
    readonly_fields = ['created_at', 'updated_at', 'images_count_display']
    inlines = [ProjectImageInline]
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('code_1c', 'name', 'title', 'description')
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
            url = reverse('admin:api_projectimage_changelist')
            return format_html(
                '<a href="{}?project__id__exact={}">{} ta</a>',
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


@admin.register(ImageStatus)
class ImageStatusAdmin(admin.ModelAdmin):
    """ImageStatus admin"""
    list_display = ['code', 'name', 'icon', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'is_deleted']
    search_fields = ['code', 'name', 'description']
    ordering = ['order', 'name']
    list_editable = ['order', 'is_active']
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('code', 'name', 'description', 'icon', 'order')
        }),
        ('Status', {
            'fields': ('is_active', 'is_deleted')
        }),
        ('Vaqt', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ImageSource)
class ImageSourceAdmin(admin.ModelAdmin):
    """ImageSource admin"""
    list_display = ['uploader_name', 'uploader_type', 'upload_location', 'is_active', 'created_at']
    list_filter = ['uploader_type', 'is_active', 'is_deleted', 'created_at']
    search_fields = ['uploader_name', 'uploader_contact', 'upload_location']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Yuboruvchi ma\'lumotlari', {
            'fields': ('uploader_name', 'uploader_type', 'uploader_contact')
        }),
        ('Yuklash ma\'lumotlari', {
            'fields': ('upload_location', 'upload_device', 'notes')
        }),
        ('Status', {
            'fields': ('is_active', 'is_deleted')
        }),
        ('Vaqt', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    """ProjectImage admin"""
    list_display = ['image_preview', 'project', 'category', 'status', 'is_main', 'is_active', 'is_deleted', 'created_at']
    list_filter = ['category', 'status', 'is_main', 'is_active', 'is_deleted', 'project', 'created_at']
    search_fields = ['project__name', 'project__code_1c']
    readonly_fields = ['image_preview', 'created_at', 'updated_at']
    list_per_page = 25
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('project', 'image', 'image_preview', 'is_main', 'category', 'note')
        }),
        ('Rasm ma\'lumotlari', {
            'fields': ('status', 'source')
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
        """Optimizatsiya: select_related bilan project yuklash"""
        return super().get_queryset(request).select_related('project')
