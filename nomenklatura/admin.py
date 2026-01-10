from django.contrib import admin
from django.db.models import Q
from django.utils.html import format_html
from django.urls import reverse
from .models import Nomenklatura, NomenklaturaImage


class NomenklaturaImageInline(admin.TabularInline):
    """NomenklaturaImage inline admin"""
    model = NomenklaturaImage
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


class ImageStatusFilter(admin.SimpleListFilter):
    title = "Rasm holati"
    parameter_name = "image_status"

    def lookups(self, request, model_admin):
        return (
            ("with", "Rasm bor"),
            ("without", "Rasm yo'q"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == "with":
            # Rasmlari bor bo'lganlar
            return queryset.filter(images__is_deleted=False).distinct()
        if value == "without":
            # Rasmlari yo'q bo'lganlar
            return queryset.exclude(images__is_deleted=False).distinct()
        return queryset


@admin.register(Nomenklatura)
class NomenklaturaAdmin(admin.ModelAdmin):
    """Nomenklatura admin"""
    list_display = ['name', 'code_1c', 'get_projects', 'sku', 'brand', 'category', 'base_price', 'stock_quantity', 'rating', 'images_count', 'is_active', 'is_deleted', 'created_at']
    list_filter = ['is_active', 'is_deleted', 'projects', DescriptionStatusFilter, ImageStatusFilter, 'category', 'subcategory', 'brand', 'manufacturer', 'created_at', 'updated_at']
    search_fields = ['name', 'code_1c', 'title', 'sku', 'barcode', 'brand', 'manufacturer', 'model', 'category']
    readonly_fields = ['created_at', 'updated_at', 'images_count_display']
    inlines = [NomenklaturaImageInline]
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('code_1c', 'name', 'projects', 'title', 'description')
        }),
        ('Mahsulot identifikatsiyasi', {
            'fields': ('sku', 'barcode', 'brand', 'manufacturer', 'model', 'series', 'vendor_code'),
            'classes': ('collapse',)
        }),
        ('Narx ma\'lumotlari', {
            'fields': ('base_price', 'sale_price', 'cost_price', 'currency', 'discount_percent', 'tax_rate'),
            'classes': ('collapse',)
        }),
        ('Ombor ma\'lumotlari', {
            'fields': ('stock_quantity', 'min_stock', 'max_stock', 'unit_of_measure', 'weight', 'dimensions', 'volume'),
            'classes': ('collapse',)
        }),
        ('Kategoriya va teg', {
            'fields': ('category', 'subcategory', 'tags'),
            'classes': ('collapse',)
        }),
        ('Texnik xususiyatlar', {
            'fields': ('color', 'size', 'material', 'warranty_period', 'expiry_date', 'production_date'),
            'classes': ('collapse',)
        }),
        ('Qo\'shimcha ma\'lumotlar', {
            'fields': ('notes', 'rating', 'popularity_score', 'seo_keywords', 'source', 'metadata'),
            'classes': ('collapse',)
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
        """Optimizatsiya: prefetch_related bilan images va projects yuklash"""
        return super().get_queryset(request).prefetch_related('images', 'projects')

    def get_projects(self, obj):
        return ", ".join([p.name for p in obj.projects.all()])
    get_projects.short_description = "Loyihalar"


@admin.register(NomenklaturaImage)
class NomenklaturaImageAdmin(admin.ModelAdmin):
    """NomenklaturaImage admin"""
    list_display = ['image_preview', 'nomenklatura', 'category', 'status', 'is_main', 'is_active', 'is_deleted', 'created_at']
    list_filter = ['category', 'status', 'is_main', 'is_active', 'is_deleted', 'nomenklatura', 'created_at']
    search_fields = ['nomenklatura__name', 'nomenklatura__code_1c']
    readonly_fields = ['image_preview', 'created_at', 'updated_at']
    list_per_page = 25
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('nomenklatura', 'image', 'image_preview', 'is_main', 'category', 'note')
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
        """Optimizatsiya: select_related bilan nomenklatura yuklash"""
        return super().get_queryset(request).select_related('nomenklatura')
