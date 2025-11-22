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
    code_1c = models.CharField(max_length=255, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = RichTextField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['is_deleted', 'is_active']),
            models.Index(fields=['code_1c', 'is_deleted']),
            models.Index(fields=['name', 'is_deleted']),
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
        ]

