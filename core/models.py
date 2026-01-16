from django.db import models
from django.utils import timezone
from django.conf import settings

class BaseModel(models.Model):
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class ImportLog(BaseModel):
    """Excel import jarayonlarini kuzatish uchun log"""
    ENTITY_CHOICES = [
        ('nomenklatura', 'Nomenklatura'),
        ('client', 'Client'),
        ('project', 'Project'),
    ]
    
    entity_type = models.CharField(max_length=50, choices=ENTITY_CHOICES)
    filename = models.CharField(max_length=255)
    status = models.CharField(
        max_length=50,
        choices=[
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('error', 'Error'),
        ],
        default='processing'
    )
    
    total_rows = models.IntegerField(default=0)
    created_count = models.IntegerField(default=0)
    updated_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    
    errors_json = models.JSONField(default=list, blank=True, help_text="Qatorlar bo'yicha xatoliklar")
    summary = models.TextField(blank=True, null=True)
    
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='import_logs'
    )

    class Meta:
        verbose_name = "Import Log"
        verbose_name_plural = "Import Logs"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_entity_type_display()} - {self.filename} - {self.status}"

class ErrorLog(BaseModel):
    """Tizimda yuz bergan kutilmagan xatoliklarni saqlash uchun log"""
    error_type = models.CharField(max_length=255)
    message = models.TextField()
    stack_trace = models.TextField(blank=True, null=True)
    
    path = models.CharField(max_length=255, blank=True, null=True)
    method = models.CharField(max_length=10, blank=True, null=True)
    query_params = models.JSONField(default=dict, blank=True)
    request_data = models.TextField(blank=True, null=True)
    
    user_agent = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='error_logs'
    )

    class Meta:
        verbose_name = "Error Log"
        verbose_name_plural = "Error Logs"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.error_type}: {self.message[:50]}"
