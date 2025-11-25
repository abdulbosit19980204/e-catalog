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


class AgentLocation(BaseModel):
    """Mobil agentlar tomonidan yuborilgan geolokatsiya yozuvlari"""

    agent_code = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Agentni identifikatsiya qilish uchun code (unikal emas, lekin tez-tez ishlatiladi)"
    )
    agent_name = models.CharField(max_length=150, blank=True, default='', help_text="Agent to'liq ismi")
    agent_phone = models.CharField(max_length=50, blank=True, default='', help_text="Aloqa telefoni")
    region = models.CharField(max_length=120, blank=True, default='', help_text="Hudud yoki filial nomi")

    # Device ma'lumotlari
    device_id = models.CharField(max_length=120, blank=True, default='', help_text="Qurilma ID (IMEI yoki UUID)")
    device_name = models.CharField(max_length=120, blank=True, default='', help_text="Qurilma nomi/modeli")
    device_manufacturer = models.CharField(max_length=100, blank=True, default='', help_text="Ishlab chiqaruvchi (Samsung, Apple, Xiaomi, etc.)")
    device_model = models.CharField(max_length=100, blank=True, default='', help_text="Qurilma modeli (SM-G991B, iPhone 13, etc.)")
    platform = models.CharField(max_length=50, blank=True, default='', help_text="Operatsion tizim (Android/iOS)")
    os_version = models.CharField(max_length=50, blank=True, default='', help_text="OS versiyasi (Android 12, iOS 15.0, etc.)")
    screen_width = models.IntegerField(blank=True, null=True, help_text="Ekran kengligi (pixel)")
    screen_height = models.IntegerField(blank=True, null=True, help_text="Ekran balandligi (pixel)")
    screen_density = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Ekran zichligi (DPI)")
    ram_total = models.BigIntegerField(blank=True, null=True, help_text="Jami RAM (byte)")
    ram_available = models.BigIntegerField(blank=True, null=True, help_text="Mavjud RAM (byte)")
    storage_total = models.BigIntegerField(blank=True, null=True, help_text="Jami xotira (byte)")
    storage_available = models.BigIntegerField(blank=True, null=True, help_text="Mavjud xotira (byte)")
    camera_front = models.BooleanField(default=False, help_text="Old kamera mavjudligi")
    camera_back = models.BooleanField(default=False, help_text="Orqa kamera mavjudligi")
    camera_resolution = models.CharField(max_length=50, blank=True, default='', help_text="Kamera o'lchami (masalan: 12MP)")
    
    # App ma'lumotlari
    app_version = models.CharField(max_length=40, blank=True, default='', help_text="Mobil ilova versiyasi")
    app_build_number = models.CharField(max_length=50, blank=True, default='', help_text="Build raqami")
    app_installation_date = models.DateTimeField(blank=True, null=True, help_text="Ilova o'rnatilgan sana")
    app_last_update = models.DateTimeField(blank=True, null=True, help_text="Ilova oxirgi yangilangan sana")

    # Lokatsiya ma'lumotlari
    latitude = models.DecimalField(max_digits=9, decimal_places=6, help_text="Latitude (WGS84)")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, help_text="Longitude (WGS84)")
    accuracy = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, help_text="Aniqlik (metr)")
    altitude = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, help_text="Balandlik (m)")
    speed = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, help_text="Tezlik (m/s)")
    heading = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, help_text="Yo'nalish (gradus)")
    city = models.CharField(max_length=100, blank=True, default='', help_text="Shahar nomi")
    country = models.CharField(max_length=100, blank=True, default='', help_text="Davlat nomi")
    postal_code = models.CharField(max_length=20, blank=True, default='', help_text="Pochta indeksi")
    timezone = models.CharField(max_length=50, blank=True, default='', help_text="Vaqt mintaqasi (UTC+5, Asia/Tashkent, etc.)")
    location_provider = models.CharField(max_length=50, blank=True, default='', help_text="Lokatsiya manbasi (GPS, Network, Passive)")

    # Batareya ma'lumotlari
    battery_level = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        blank=True,
        null=True,
        help_text="Batareya (%)"
    )
    is_charging = models.BooleanField(default=False)
    battery_health = models.CharField(max_length=50, blank=True, default='', help_text="Batareya holati (Good, Fair, Poor, etc.)")
    battery_temperature = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Batareya harorati (°C)")
    battery_voltage = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True, help_text="Batareya kuchlanishi (V)")
    
    # Tarmoq ma'lumotlari
    signal_strength = models.CharField(max_length=50, blank=True, default='', help_text="Signal kuchi yoki operator")
    network_type = models.CharField(max_length=50, blank=True, default='', help_text="Tarmoq turi (WiFi, 4G, 5G, LTE, etc.)")
    wifi_ssid = models.CharField(max_length=100, blank=True, default='', help_text="WiFi tarmoq nomi (SSID)")
    wifi_bssid = models.CharField(max_length=50, blank=True, default='', help_text="WiFi BSSID (MAC address)")
    cellular_operator = models.CharField(max_length=100, blank=True, default='', help_text="Mobil operator nomi")
    cellular_network_type = models.CharField(max_length=50, blank=True, default='', help_text="Mobil tarmoq turi (GSM, CDMA, LTE, etc.)")
    ip_address = models.GenericIPAddressField(blank=True, null=True, help_text="IP manzil")
    connection_type = models.CharField(max_length=50, blank=True, default='', help_text="Ulanish turi (WiFi, Mobile, Ethernet, etc.)")

    # Sensor ma'lumotlari
    accelerometer_x = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True, help_text="Accelerometer X (m/s²)")
    accelerometer_y = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True, help_text="Accelerometer Y (m/s²)")
    accelerometer_z = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True, help_text="Accelerometer Z (m/s²)")
    gyroscope_x = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True, help_text="Gyroscope X (rad/s)")
    gyroscope_y = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True, help_text="Gyroscope Y (rad/s)")
    gyroscope_z = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True, help_text="Gyroscope Z (rad/s)")
    magnetometer_x = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True, help_text="Magnetometer X (μT)")
    magnetometer_y = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True, help_text="Magnetometer Y (μT)")
    magnetometer_z = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True, help_text="Magnetometer Z (μT)")
    proximity_sensor = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True, help_text="Proximity sensor (cm)")
    light_sensor = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, help_text="Yorug'lik sensori (lux)")
    
    # Atrof-muhit ma'lumotlari
    temperature = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Harorat (°C)")
    humidity = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Namlik (%)")
    pressure = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, help_text="Bosim (hPa)")
    
    # Xavfsizlik ma'lumotlari
    device_fingerprint = models.CharField(max_length=255, blank=True, default='', help_text="Qurilma fingerprint (hash)")
    is_rooted = models.BooleanField(default=False, help_text="Qurilma root qilinganmi")
    is_jailbroken = models.BooleanField(default=False, help_text="Qurilma jailbreak qilinganmi (iOS)")
    encryption_enabled = models.BooleanField(default=False, help_text="Shifrlash yoqilganmi")
    screen_lock_type = models.CharField(max_length=50, blank=True, default='', help_text="Ekran qulfi turi (None, PIN, Pattern, Fingerprint, Face, etc.)")
    
    # Vaqt va manzil
    logged_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Agent qurilmasida yozilgan vaqt (agar mavjud bo'lsa)"
    )
    address = models.CharField(max_length=255, blank=True, default='', help_text="Geo reverse address")
    note = models.TextField(blank=True, default='', help_text="Qo'shimcha izoh")
    metadata = models.JSONField(blank=True, null=True, default=dict, help_text="Qo'shimcha meta ma'lumotlar (JSON)")

    class Meta:
        verbose_name = "Agent Location"
        verbose_name_plural = "Agent Locations"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['agent_code', 'created_at']),
            models.Index(fields=['is_deleted', 'is_active']),
        ]

    def __str__(self):
        return f"{self.agent_code} ({self.latitude}, {self.longitude})"
