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

class Client(BaseModel):
    client_code_1c = models.CharField(max_length=100, db_index=True)
    name = models.CharField(max_length=100, db_index=True)
    email = models.EmailField(max_length=100, blank=True, null=True, db_index=True)
    phone = models.CharField(max_length=100, blank=True, null=True)
    description = RichTextField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['is_deleted', 'is_active']),
            models.Index(fields=['client_code_1c', 'is_deleted']),
            models.Index(fields=['name', 'is_deleted']),
            models.Index(fields=['email', 'is_deleted']),
        ]

    def __str__(self):
        return self.name

class ClientImage(BaseModel):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='images', db_index=True)
    image = models.ImageField(upload_to='clients/')
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
        return self.client.name
    
    class Meta:
        verbose_name_plural = "Client Images"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['client', 'is_deleted']),
            models.Index(fields=['is_main', 'is_deleted']),
        ]
