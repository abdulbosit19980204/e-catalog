from django.db import models
from ckeditor.fields import RichTextField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

# Create your models here.
class BaseModel(models.Model):
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class Nomenklatura(BaseModel):
    project = models.ForeignKey('api.Project', on_delete=models.CASCADE, related_name='nomenclatures', blank=True, null=True, help_text="Proyekt")
    code_1c = models.CharField(max_length=255, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = RichTextField(blank=True, null=True)
    
    # Product Information
    sku = models.CharField(max_length=100, blank=True, null=True, db_index=True, help_text="SKU (Stock Keeping Unit)")
    article_code = models.CharField(max_length=100, blank=True, null=True, db_index=True, help_text="Artikul kodi")
    barcode = models.CharField(max_length=100, blank=True, null=True, db_index=True, help_text="Barkod")
    brand = models.CharField(max_length=150, blank=True, null=True, help_text="Brend")
    manufacturer = models.CharField(max_length=200, blank=True, null=True, help_text="Ishlab chiqaruvchi")
    model = models.CharField(max_length=150, blank=True, null=True, help_text="Model")
    series = models.CharField(max_length=150, blank=True, null=True, help_text="Seriya")
    vendor_code = models.CharField(max_length=100, blank=True, null=True, help_text="Sotuvchi kodi")
    
    # Pricing Information
    base_price = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, help_text="Asosiy narx")
    sale_price = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, help_text="Sotuv narxi")
    cost_price = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, help_text="Narx (xarajat)")
    currency = models.CharField(max_length=10, blank=True, null=True, default='UZS', help_text="Valyuta")
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Chegirma foizi")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="QQS foizi")
    
    # Inventory Information
    stock_quantity = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Ombor miqdori")
    min_stock = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Minimal ombor")
    max_stock = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Maksimal ombor")
    unit_of_measure = models.CharField(max_length=50, blank=True, null=True, help_text="O'lchov birligi")
    weight = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True, help_text="Og'irlik (kg)")
    dimensions = models.CharField(max_length=100, blank=True, null=True, help_text="O'lchamlari (LxWxH)")
    volume = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True, help_text="Hajm (m³)")
    
    # Category Information
    category = models.CharField(max_length=150, blank=True, null=True, db_index=True, help_text="Kategoriya")
    subcategory = models.CharField(max_length=150, blank=True, null=True, help_text="Quyi kategoriya")
    tags = models.JSONField(blank=True, null=True, default=list, help_text="Teglar (JSON)")
    
    # Specifications
    color = models.CharField(max_length=100, blank=True, null=True, help_text="Rang")
    size = models.CharField(max_length=100, blank=True, null=True, help_text="O'lcham")
    material = models.CharField(max_length=200, blank=True, null=True, help_text="Material")
    warranty_period = models.IntegerField(blank=True, null=True, help_text="Kafolat muddati (oy)")
    expiry_date = models.DateField(blank=True, null=True, help_text="Yaroqlilik muddati")
    production_date = models.DateField(blank=True, null=True, help_text="Ishlab chiqarilgan sana")
    
    # Additional Information
    roditel = models.CharField(max_length=255, blank=True, null=True, help_text="Roditel (1C)")
    supplier = models.CharField(max_length=255, blank=True, null=True, help_text="Yetkazib beruvchi")
    country_code = models.CharField(max_length=10, blank=True, null=True, help_text="Davlat kodi")
    country = models.CharField(max_length=150, blank=True, null=True, help_text="Ishlab chiqarilgan davlat")
    
    notes = models.TextField(blank=True, null=True, help_text="Qo'shimcha izohlar")
    rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True, help_text="Reyting (0-5)")
    popularity_score = models.IntegerField(blank=True, null=True, default=0, help_text="Mashhurligi (0-100)")
    seo_keywords = models.CharField(max_length=500, blank=True, null=True, help_text="SEO kalit so'zlar")
    source = models.CharField(max_length=100, blank=True, null=True, help_text="Manba")
    metadata = models.JSONField(blank=True, null=True, default=dict, help_text="Qo'shimcha meta ma'lumotlar (JSON)")

    class Meta:
        unique_together = ('project', 'code_1c')
        indexes = [
            models.Index(fields=['is_deleted', 'is_active']),
            models.Index(fields=['project', 'code_1c', 'is_deleted']),
            models.Index(fields=['name', 'is_deleted']),
            models.Index(fields=['sku', 'barcode']),
            models.Index(fields=['category', 'is_deleted']),
            models.Index(fields=['brand', 'is_deleted']),
            models.Index(fields=['base_price', 'is_deleted']),
            models.Index(fields=['created_at', 'is_deleted']),
            models.Index(fields=['rating', 'popularity_score']),
        ]

    def __str__(self):
        return self.name

class NomenklaturaImage(BaseModel):
    nomenklatura = models.ForeignKey(Nomenklatura, on_delete=models.CASCADE, related_name='images', db_index=True)
    image = models.ImageField(upload_to='nomenklatura/')
    is_main = models.BooleanField(default=False, db_index=True)
    category = models.CharField(
        max_length=120,
        blank=True,
        default='',
        help_text="Rasm toifasi yoki teg"
    )
    note = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text="Rasm haqida qo'shimcha izoh"
    )
    status = models.ForeignKey(
        'api.ImageStatus',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='nomenklatura_images',
        db_index=True,
        help_text="Rasm statusi"
    )
    source = models.ForeignKey(
        'api.ImageSource',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='nomenklatura_images',
        db_index=True,
        help_text="Rasmni yuboruvchi ma'lumotlari"
    )
    
    # Turli o'lchamlarda rasmlar
    image_sm = ImageSpecField(
        source='image',
        processors=[ResizeToFill(300, 300)],
        format='JPEG',
        options={'quality': 85}
    )
    image_md = ImageSpecField(
        source='image',
        processors=[ResizeToFill(600, 600)],
        format='JPEG',
        options={'quality': 85}
    )
    image_lg = ImageSpecField(
        source='image',
        processors=[ResizeToFill(1200, 1200)],
        format='JPEG',
        options={'quality': 90}
    )
    image_thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(150, 150)],
        format='JPEG',
        options={'quality': 80}
    )

    def __str__(self):
        return self.nomenklatura.name

    class Meta:
        verbose_name_plural = "Nomenklatura Images"
        ordering = ['-created_at']
        verbose_name = "Nomenklatura Image"
        indexes = [
            models.Index(fields=['nomenklatura', 'is_deleted']),
            models.Index(fields=['is_main', 'is_deleted']),
            models.Index(fields=['created_at', 'is_deleted']),
        ]

    def save(self, *args, **kwargs):
        if self.is_main:
            # Ushbu nomenklatura uchun boshqa barcha rasmlarni is_main=False qilish
            NomenklaturaImage.objects.filter(
                nomenklatura=self.nomenklatura, 
                is_main=True
            ).exclude(pk=self.pk).update(is_main=False)
        super().save(*args, **kwargs)

