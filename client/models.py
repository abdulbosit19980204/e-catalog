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
    
    # Company Information
    company_name = models.CharField(max_length=255, blank=True, null=True, help_text="Kompaniya nomi")
    tax_id = models.CharField(max_length=50, blank=True, null=True, help_text="INN/STIR")
    registration_number = models.CharField(max_length=100, blank=True, null=True, help_text="Ro'yxatdan o'tish raqami")
    legal_address = models.TextField(blank=True, null=True, help_text="Yuridik manzil")
    actual_address = models.TextField(blank=True, null=True, help_text="Haqiqiy manzil")
    
    # Contact Information
    fax = models.CharField(max_length=50, blank=True, null=True, help_text="Faks raqami")
    website = models.URLField(max_length=255, blank=True, null=True, help_text="Veb-sayt")
    social_media = models.JSONField(blank=True, null=True, default=dict, help_text="Ijtimoiy tarmoqlar (JSON)")
    additional_phones = models.JSONField(blank=True, null=True, default=list, help_text="Qo'shimcha telefon raqamlari (JSON)")
    
    # Business Information
    industry = models.CharField(max_length=150, blank=True, null=True, help_text="Soha/Industriya")
    business_type = models.CharField(max_length=100, blank=True, null=True, help_text="Biznes turi")
    employee_count = models.IntegerField(blank=True, null=True, help_text="Xodimlar soni")
    annual_revenue = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, help_text="Yillik daromad")
    established_date = models.DateField(blank=True, null=True, help_text="Tashkil etilgan sana")
    
    # Financial Information
    payment_terms = models.CharField(max_length=255, blank=True, null=True, help_text="To'lov shartlari")
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, help_text="Kredit limiti")
    currency = models.CharField(max_length=10, blank=True, null=True, default='UZS', help_text="Valyuta")
    
    # Location Information
    city = models.CharField(max_length=100, blank=True, null=True, help_text="Shahar")
    region = models.CharField(max_length=100, blank=True, null=True, help_text="Viloyat/Hudud")
    country = models.CharField(max_length=100, blank=True, null=True, default='Uzbekistan', help_text="Davlat")
    postal_code = models.CharField(max_length=20, blank=True, null=True, help_text="Pochta indeksi")
    
    # Contact Person
    contact_person = models.CharField(max_length=150, blank=True, null=True, help_text="Kontakt shaxs")
    contact_position = models.CharField(max_length=100, blank=True, null=True, help_text="Lavozim")
    contact_email = models.EmailField(max_length=100, blank=True, null=True, help_text="Kontakt email")
    contact_phone = models.CharField(max_length=100, blank=True, null=True, help_text="Kontakt telefon")
    
    # Additional Information
    notes = models.TextField(blank=True, null=True, help_text="Qo'shimcha izohlar")
    tags = models.JSONField(blank=True, null=True, default=list, help_text="Teglar (JSON)")
    rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True, help_text="Reyting (0-5)")
    priority = models.IntegerField(blank=True, null=True, default=0, help_text="Prioritet (0-100)")
    source = models.CharField(max_length=100, blank=True, null=True, help_text="Manba")
    metadata = models.JSONField(blank=True, null=True, default=dict, help_text="Qo'shimcha meta ma'lumotlar (JSON)")

    class Meta:
        indexes = [
            models.Index(fields=['is_deleted', 'is_active']),
            models.Index(fields=['client_code_1c', 'is_deleted']),
            models.Index(fields=['name', 'is_deleted']),
            models.Index(fields=['email', 'is_deleted']),
            models.Index(fields=['city', 'region']),
            models.Index(fields=['industry', 'business_type']),
            models.Index(fields=['rating', 'priority']),
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
    status = models.ForeignKey(
        'api.ImageStatus',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='client_images',
        db_index=True,
        help_text="Rasm statusi"
    )
    source = models.ForeignKey(
        'api.ImageSource',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='client_images',
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
        return self.client.name
    
    class Meta:
        verbose_name_plural = "Client Images"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['client', 'is_deleted']),
            models.Index(fields=['is_main', 'is_deleted']),
            models.Index(fields=['created_at', 'is_deleted']),
        ]

    def save(self, *args, **kwargs):
        if self.is_main:
            # Ushbu client uchun boshqa barcha rasmlarni is_main=False qilish
            ClientImage.objects.filter(
                client=self.client, 
                is_main=True
            ).exclude(pk=self.pk).update(is_main=False)
        super().save(*args, **kwargs)
