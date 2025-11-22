from django.db import models
from ckeditor.fields import RichTextField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, ResizeToFit

# Create your models here.
class BaseModel(models.Model):
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True


class ImageStatus(BaseModel):
    """Rasm statuslari uchun alohida table"""
    code = models.CharField(
        max_length=50, 
        unique=True, 
        db_index=True,
        help_text="Status kodi (masalan: 'store_before', 'store_after', 'product_main')"
    )
    name = models.CharField(
        max_length=100,
        help_text="Status nomi (masalan: 'Magazin - Tashrif oldidan', 'Magazin - Tashrifdan keyin')"
    )
    description = models.TextField(
        blank=True, 
        null=True,
        help_text="Status haqida batafsil ma'lumot"
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        default='',
        help_text="Icon nomi yoki emoji (masalan: 'store', 'product', 'info')"
    )
    order = models.IntegerField(
        default=0,
        help_text="Tartib raqami (admin panelda ko'rinish tartibi)"
    )
    
    class Meta:
        verbose_name = "Image Status"
        verbose_name_plural = "Image Statuses"
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['code', 'is_deleted']),
            models.Index(fields=['is_active', 'is_deleted']),
        ]
    
    def __str__(self):
        return self.name


class ImageSource(BaseModel):
    """Rasmni yuboruvchi ma'lumotlari"""
    uploader_name = models.CharField(
        max_length=100,
        help_text="Yuboruvchi ismi (masalan: 'Agent: John Doe', 'Client: ABC Company')"
    )
    uploader_type = models.CharField(
        max_length=50,
        choices=[
            ('agent', 'Agent'),
            ('client', 'Client'),
            ('admin', 'Administrator'),
            ('system', 'System'),
            ('other', 'Other'),
        ],
        default='other',
        help_text="Yuboruvchi turi"
    )
    uploader_contact = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Yuboruvchi kontakt ma'lumotlari (telefon, email, va hokazo)"
    )
    upload_location = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Rasm yuklangan joy (masalan: 'Toshkent, Chilonzor', 'Mobile App', 'Web Admin')"
    )
    upload_device = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Qurilma ma'lumotlari (masalan: 'iPhone 12', 'Samsung Galaxy', 'Web Browser')"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Qo'shimcha izohlar"
    )
    
    class Meta:
        verbose_name = "Image Source"
        verbose_name_plural = "Image Sources"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['uploader_type', 'is_deleted']),
            models.Index(fields=['is_active', 'is_deleted']),
        ]
    
    def __str__(self):
        return f"{self.uploader_name} ({self.get_uploader_type_display()})"

class Project(BaseModel):
    code_1c = models.CharField(max_length=255, unique=True, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = RichTextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_deleted', 'is_active']),
            models.Index(fields=['code_1c', 'is_deleted']),
            models.Index(fields=['name', 'is_deleted']),
        ]

    def __str__(self):
        return self.name

class ProjectImage(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images', db_index=True)
    image = models.ImageField(upload_to='projects/')
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
        'ImageStatus',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='project_images',
        db_index=True,
        help_text="Rasm statusi"
    )
    source = models.ForeignKey(
        'ImageSource',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='project_images',
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
        return f"{self.project.name} - Image"

    class Meta:
        verbose_name_plural = "Project Images"
        ordering = ['-created_at']
        verbose_name = "Project Image"
        indexes = [
            models.Index(fields=['project', 'is_deleted']),
            models.Index(fields=['is_main', 'is_deleted']),
        ]
