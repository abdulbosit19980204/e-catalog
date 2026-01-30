from django.db import models
from django.utils import timezone
import uuid

class AppLicense(models.Model):
    ENTITY_TYPES = (
        ('USER', 'User'),
        ('ORGANIZATION', 'Organization'),
        ('PROJECT', 'Project'),
    )
    
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('REVOKED', 'Revoked'),
        ('PENDING', 'Pending'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPES, default='USER')
    entity_id = models.IntegerField(help_text="Linked Entity ID (e.g. User ID, Project ID)")
    license_key = models.CharField(max_length=50, unique=True)
    device_id = models.CharField(max_length=255, null=True, blank=True, help_text="Unique device identifier")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    starts_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_unlimited = models.BooleanField(default=False)
    activation_count = models.IntegerField(default=0, help_text="Number of times activated")
    last_activated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def generate_license_key(organization_name="App"):
        """Generate unique license key like 'Gloriya_2025_XT_SV-SS'"""
        import random
        import string
        from datetime import datetime
        
        year = datetime.now().year
        random_part = ''.join(random.choices(string.ascii_uppercase, k=2))
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=2))
        random_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=2))
        
        return f"{organization_name}_{year}_{random_part}_{random_suffix}-{random_code}"

    def __str__(self):
        return f"{self.license_key} ({self.entity_type}: {self.entity_id})"

    class Meta:
        verbose_name = "App License"
        verbose_name_plural = "App Licenses"

class AppVersionMetadata(models.Model):
    version_code = models.CharField(max_length=20, unique=True, help_text="e.g. 1.0.4")
    is_mandatory_update = models.BooleanField(default=False)
    min_supported_os = models.CharField(max_length=50, null=True, blank=True)
    release_notes = models.TextField(null=True, blank=True)
    release_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.version_code

    class Meta:
        verbose_name = "App Version"
        verbose_name_plural = "App Versions"

class AccessHistory(models.Model):
    REQUEST_TYPES = (
        ('ACTIVATION', 'Activation'),
        ('STATUS_CHECK', 'Status Check'),
        ('VERSION_ACTIVATION', 'Version Activation'),
    )
    
    license = models.ForeignKey(AppLicense, on_delete=models.CASCADE, related_name='history')
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    version = models.CharField(max_length=20)
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES, default='STATUS_CHECK')
    device_info = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    accessed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.license.license_key} - {self.request_type} - {self.version} at {self.accessed_at}"

    class Meta:
        verbose_name = "Access History"
        verbose_name_plural = "Access Histories"
