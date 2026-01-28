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

class SystemSettings(BaseModel):
    """Dynamically configurable system settings (e.g., API keys)"""
    FIELD_TYPE_CHOICES = [
        ('text', 'Text'),
        ('secret', 'Secret Key'),
        ('select', 'Selection'),
        ('multiselect', 'Multi-Selection'),
        ('number', 'Number'),
    ]
    
    key = models.CharField(max_length=255, unique=True, help_text="Config key (e.g. GEMINI_API_KEY)")
    value = models.TextField(help_text="Config value")
    field_type = models.CharField(max_length=20, choices=FIELD_TYPE_CHOICES, default='text')
    options = models.JSONField(blank=True, null=True, help_text="Possible values for 'select' type")
    description = models.CharField(max_length=500, blank=True, null=True, help_text="Key description")
    is_secret = models.BooleanField(default=True, help_text="If true, value is sensitive (API key, etc.)")

    class Meta:
        verbose_name = "System Setting"
        verbose_name_plural = "System Settings"
        ordering = ['key']

    def __str__(self):
        return self.key

class AITokenUsage(BaseModel):
    """Tracks token usage for AI operations"""
    model_name = models.CharField(max_length=100)
    input_tokens = models.IntegerField(default=0)
    output_tokens = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)
    purpose = models.CharField(max_length=255, blank=True, null=True, help_text="e.g. Nomenklatura Description")
    
    # Cost calculation (optional, can be done at runtime)
    cost = models.DecimalField(max_digits=12, decimal_places=6, default=0)

    class Meta:
        verbose_name = "AI Token Usage"
        verbose_name_plural = "AI Token Usage Logs"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.model_name} - {self.total_tokens} tokens"

class AIModel(BaseModel):
    """Database of available AI Models (LLMs)"""
    PROVIDER_CHOICES = [
        ('google', 'Google (Gemini)'),
        ('puter', 'Puter.com (Free)'),
        ('openai', 'OpenAI (GPT)'),
        ('anthropic', 'Anthropic (Claude)'),
        ('custom', 'Custom Provider'),
    ]
    
    name = models.CharField(max_length=100, help_text="Human-readable name")
    model_id = models.CharField(max_length=255, unique=True, help_text="API identifier (e.g. models/gemini-1.5-pro)")
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES, default='google')
    is_default = models.BooleanField(default=False)
    meta_data = models.JSONField(default=dict, blank=True, help_text="Additional params (temperature, etc.)")

    class Meta:
        verbose_name = "AI Model"
        verbose_name_plural = "AI Models"
        ordering = ['-is_default', 'name']

    def __str__(self):
        return f"{self.name} ({self.model_id})"

    def save(self, *args, **kwargs):
        if self.is_default:
            # Only one model can be default
            AIModel.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
