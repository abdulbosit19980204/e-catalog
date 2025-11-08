from django.contrib import admin
from django.db.models import Q
from django.utils.html import format_html
from django.urls import reverse
from .models import Nomenklatura, NomenklaturaImage


class NomenklaturaImageInline(admin.TabularInline):
    """NomenklaturaImage inline admin"""
    model = NomenklaturaImage
    extra = 1
    fields = ('image', 'image_preview', 'is_main', 'category', 'note', 'is_active')
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


@admin.register(Nomenklatura)
class NomenklaturaAdmin(admin.ModelAdmin):
    """Nomenklatura admin"""
    list_display = ['name', 'code_1c', 'title', 'images_count', 'is_active', 'is_deleted', 'created_at']
    list_filter = ['is_active', 'is_deleted', DescriptionStatusFilter, 'created_at', 'updated_at']
    search_fields = ['name', 'code_1c', 'title']
    readonly_fields = ['created_at', 'updated_at', 'images_count_display']
    inlines = [NomenklaturaImageInline]
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
            url = reverse('admin:nomenklatura_nomenklaturaimage_changelist')
            return format_html(
                '<a href="{}?nomenklatura__id__exact={}">{} ta</a>',
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


@admin.register(NomenklaturaImage)
class NomenklaturaImageAdmin(admin.ModelAdmin):
    """NomenklaturaImage admin"""
    list_display = ['image_preview', 'nomenklatura', 'category', 'is_main', 'is_active', 'is_deleted', 'created_at']
    list_filter = ['category', 'is_main', 'is_active', 'is_deleted', 'nomenklatura', 'created_at']
    search_fields = ['nomenklatura__name', 'nomenklatura__code_1c']
    readonly_fields = ['image_preview', 'created_at', 'updated_at']
    list_per_page = 25
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('nomenklatura', 'image', 'image_preview', 'is_main', 'category', 'note')
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
        """Optimizatsiya: select_related bilan nomenklatura yuklash"""
        return super().get_queryset(request).select_related('nomenklatura')
