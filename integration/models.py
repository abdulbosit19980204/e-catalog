from django.db import models
from ckeditor.fields import RichTextField

class BaseModel(models.Model):
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class Integration(BaseModel):
    """1C Integration sozlamalari"""
    name = models.CharField(max_length=255, unique=True, help_text="Integration nomi")
    project = models.ForeignKey(
        'api.Project',
        on_delete=models.CASCADE,
        related_name='integrations',
        help_text="Qaysi project'ga tegishli"
    )
    wsdl_url = models.URLField(
        max_length=500,
        help_text="1C Web Service WSDL URL"
    )
    username = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="SOAP Authentication Username"
    )
    password = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="SOAP Authentication Password"
    )
    method_nomenklatura = models.CharField(
        max_length=255,
        default='GetProductList',
        help_text="Nomenklatura'larni olish uchun method nomi"
    )
    method_clients = models.CharField(
        max_length=255,
        default='GetClientList',
        help_text="Client'larni olish uchun method nomi"
    )
    chunk_size = models.IntegerField(
        default=50,
        help_text="Bir vaqtda qancha ma'lumot yuklash (chunk size)"
    )
    description = RichTextField(blank=True, null=True, help_text="Integration tavsifi")
    
    class Meta:
        verbose_name = "Integration"
        verbose_name_plural = "Integrations"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'is_deleted']),
            models.Index(fields=['is_active', 'is_deleted']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.project.name}"


class IntegrationLog(BaseModel):
    """Integration sync log'lari"""
    integration = models.ForeignKey(
        Integration,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    task_id = models.CharField(max_length=255, unique=True, db_index=True)
    sync_type = models.CharField(
        max_length=50,
        choices=[
            ('nomenklatura', 'Nomenklatura'),
            ('clients', 'Clients'),
        ],
        db_index=True
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ('fetching', 'Fetching'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('error', 'Error'),
        ],
        default='fetching',
        db_index=True
    )
    total_items = models.IntegerField(default=0)
    processed_items = models.IntegerField(default=0)
    created_items = models.IntegerField(default=0)
    updated_items = models.IntegerField(default=0)
    error_items = models.IntegerField(default=0)
    message = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    error_details = models.TextField(blank=True, null=True)
    
    @property
    def total(self):
        """total_items uchun alias"""
        return self.total_items
    
    @property
    def processed(self):
        """processed_items uchun alias"""
        return self.processed_items
    
    @property
    def created(self):
        """created_items uchun alias"""
        return self.created_items
    
    @property
    def updated(self):
        """updated_items uchun alias"""
        return self.updated_items
    
    @property
    def errors(self):
        """error_items uchun alias"""
        return self.error_items
    
    @property
    def progress_percent(self):
        """Progress foizini hisoblash"""
        if self.total_items > 0:
            return int((self.processed_items / self.total_items) * 100)
        return 0
    
    @property
    def started_at(self):
        """start_time uchun alias"""
        return self.start_time
    
    @property
    def completed_at(self):
        """end_time uchun alias"""
        return self.end_time
    
    @property
    def error_message(self):
        """error_details uchun alias"""
        return self.error_details
    
    class Meta:
        verbose_name = "Integration Log"
        verbose_name_plural = "Integration Logs"
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['integration', 'status']),
            models.Index(fields=['task_id']),
            models.Index(fields=['sync_type', 'status']),
        ]
    
    def __str__(self):
        return f"{self.integration.name} - {self.sync_type} - {self.status}"
