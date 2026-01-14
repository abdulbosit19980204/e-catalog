"""
Visit Management Models
Enterprise-grade visit tracking system with extensible architecture
"""
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal


class BaseModel(models.Model):
    """Abstract base model with common fields"""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    
    class Meta:
        abstract = True


class VisitType(models.TextChoices):
    """Visit type classification"""
    PLANNED = 'PLANNED', 'Rejalashtirilgan'
    UNPLANNED = 'UNPLANNED', 'Rejadan tashqari'
    ADDITIONAL = 'ADDITIONAL', "Qo'shimcha"
    FOLLOW_UP = 'FOLLOW_UP', 'Takroriy tashrif'
    EMERGENCY = 'EMERGENCY', 'Shoshilinch'


class VisitStatus(models.TextChoices):
    """Visit status workflow"""
    SCHEDULED = 'SCHEDULED', 'Rejalashtirilgan'
    CONFIRMED = 'CONFIRMED', 'Tasdiqlangan'
    IN_PROGRESS = 'IN_PROGRESS', 'Jarayonda'
    COMPLETED = 'COMPLETED', 'Yakunlangan'
    CANCELLED = 'CANCELLED', 'Bekor qilingan'
    POSTPONED = 'POSTPONED', 'Kechiktirilgan'
    NO_SHOW = 'NO_SHOW', 'Kelmaganlar'


class VisitPriority(models.TextChoices):
    """Visit priority levels"""
    LOW = 'LOW', 'Past'
    MEDIUM = 'MEDIUM', "O'rta"
    HIGH = 'HIGH', 'Yuqori'
    URGENT = 'URGENT', 'Shoshilinch'


class Visit(BaseModel):
    """
    Core visit tracking model
    Tracks agent visits to client locations with full lifecycle management
    """
    # Primary identification
    visit_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    
    # Agent information
    agent_code = models.CharField(max_length=50, db_index=True)
    agent_name = models.CharField(max_length=255)
    agent_phone = models.CharField(max_length=20, blank=True)
    
    # Client reference (flexible - can be from any client app)
    client_code = models.CharField(max_length=100, db_index=True)
    client_name = models.CharField(max_length=255)
    client_address = models.TextField(blank=True)
    
    # Visit classification
    visit_type = models.CharField(
        max_length=20,
        choices=VisitType.choices,
        default=VisitType.PLANNED,
        db_index=True
    )
    visit_status = models.CharField(
        max_length=20,
        choices=VisitStatus.choices,
        default=VisitStatus.SCHEDULED,
        db_index=True
    )
    priority = models.CharField(
        max_length=10,
        choices=VisitPriority.choices,
        default=VisitPriority.MEDIUM
    )
    
    # Scheduling
    planned_date = models.DateField(db_index=True)
    planned_time = models.TimeField(null=True, blank=True)
    planned_duration_minutes = models.IntegerField(
        default=30,
        validators=[MinValueValidator(5), MaxValueValidator(480)]
    )
    
    # Actual timing
    actual_start_time = models.DateTimeField(null=True, blank=True, db_index=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True)
    
    # Location tracking
    check_in_latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )
    check_in_longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )
    check_in_address = models.TextField(blank=True)
    check_in_accuracy = models.FloatField(null=True, blank=True)  # meters
    
    check_out_latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )
    check_out_longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )
    
    # Visit details
    purpose = models.TextField(blank=True)
    tasks_planned = models.JSONField(default=list, blank=True)
    tasks_completed = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)
    
    # Outcomes
    outcome = models.TextField(blank=True)
    next_visit_date = models.DateField(null=True, blank=True)
    next_visit_notes = models.TextField(blank=True)
    
    # Ratings and feedback
    client_satisfaction = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    agent_notes = models.TextField(blank=True)
    supervisor_notes = models.TextField(blank=True)
    
    # Metadata
    cancelled_reason = models.TextField(blank=True)
    cancelled_by = models.CharField(max_length=100, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'visits'
        ordering = ['-planned_date', '-planned_time']
        indexes = [
            models.Index(fields=['agent_code', 'planned_date', 'visit_status']),
            models.Index(fields=['client_code', 'actual_start_time']),
            models.Index(fields=['visit_type', 'created_at']),
            models.Index(fields=['visit_status', 'planned_date']),
        ]
        verbose_name = 'Visit'
        verbose_name_plural = 'Visits'
    
    def __str__(self):
        return f"{self.agent_name} → {self.client_name} ({self.planned_date})"
    
    def check_in(self, latitude, longitude, accuracy=None):
        """Check in to visit location"""
        self.actual_start_time = timezone.now()
        self.check_in_latitude = Decimal(str(latitude))
        self.check_in_longitude = Decimal(str(longitude))
        self.check_in_accuracy = accuracy
        self.visit_status = VisitStatus.IN_PROGRESS
        self.save()
    
    def check_out(self, latitude=None, longitude=None):
        """Complete visit and calculate duration"""
        self.actual_end_time = timezone.now()
        if latitude and longitude:
            self.check_out_latitude = Decimal(str(latitude))
            self.check_out_longitude = Decimal(str(longitude))
        
        if self.actual_start_time:
            delta = self.actual_end_time - self.actual_start_time
            self.duration_minutes = int(delta.total_seconds() / 60)
        
        self.visit_status = VisitStatus.COMPLETED
        self.save()
    
    def cancel(self, reason, cancelled_by):
        """Cancel scheduled visit"""
        self.visit_status = VisitStatus.CANCELLED
        self.cancelled_reason = reason
        self.cancelled_by = cancelled_by
        self.cancelled_at = timezone.now()
        self.save()
    
    @property
    def is_overdue(self):
        """Check if visit is overdue"""
        if self.visit_status in [VisitStatus.SCHEDULED, VisitStatus.CONFIRMED]:
            return timezone.now().date() > self.planned_date
        return False
    
    @property
    def is_in_progress(self):
        """Check if visit is currently in progress"""
        return self.visit_status == VisitStatus.IN_PROGRESS


class VisitPlan(BaseModel):
    """
    Visit planning and scheduling
    Defines recurring visit patterns for agents
    """
    plan_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Agent and client
    agent_code = models.CharField(max_length=50, db_index=True)
    client_code = models.CharField(max_length=100, db_index=True)
    
    # Schedule pattern
    frequency = models.CharField(
        max_length=20,
        choices=[
            ('DAILY', 'Har kuni'),
            ('WEEKLY', 'Haftalik'),
            ('BIWEEKLY', 'Ikki haftada bir'),
            ('MONTHLY', 'Oylik'),
            ('QUARTERLY', 'Choraklik'),
        ],
        default='WEEKLY'
    )
    
    # Weekly schedule
    planned_weekday = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(6)],
        help_text="0=Monday, 6=Sunday"
    )
    planned_time = models.TimeField()
    duration_minutes = models.IntegerField(default=30)
    
    # Date range
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    # Configuration
    is_active = models.BooleanField(default=True, db_index=True)
    priority = models.CharField(
        max_length=10,
        choices=VisitPriority.choices,
        default=VisitPriority.MEDIUM
    )
    
    # Auto-generation settings
    auto_generate = models.BooleanField(default=True)
    generate_days_ahead = models.IntegerField(default=7)
    
    class Meta:
        db_table = 'visit_plans'
        ordering = ['agent_code', 'planned_weekday', 'planned_time']
        indexes = [
            models.Index(fields=['agent_code', 'is_active']),
            models.Index(fields=['client_code', 'is_active']),
        ]
        unique_together = [['agent_code', 'client_code', 'planned_weekday', 'planned_time']]
    
    def __str__(self):
        return f"{self.agent_code} → {self.client_code} ({self.get_frequency_display()})"


class VisitImage(BaseModel):
    """
    Images captured during visits
    Linked to both Visit and ClientImage for flexibility
    """
    image_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    visit = models.ForeignKey(
        Visit,
        on_delete=models.CASCADE,
        related_name='images',
        db_index=True
    )
    
    # Image metadata
    image_type = models.CharField(
        max_length=50,
        choices=[
            ('PRODUCT', 'Mahsulot'),
            ('SHELF', 'Javon'),
            ('STOREFRONT', "Do'kon ko'rinishi"),
            ('RECEIPT', 'Kvitansiya'),
            ('SIGNATURE', 'Imzo'),
            ('OTHER', 'Boshqa'),
        ],
        default='PRODUCT'
    )
    
    image_url = models.URLField(max_length=500)
    thumbnail_url = models.URLField(max_length=500, blank=True)
    
    # Capture details
    captured_at = models.DateTimeField(auto_now_add=True)
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )
    
    # Optional link to existing ClientImage
    client_image_id = models.IntegerField(null=True, blank=True, db_index=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'visit_images'
        ordering = ['-captured_at']
        indexes = [
            models.Index(fields=['visit', 'image_type']),
        ]
    
    def __str__(self):
        return f"Image for {self.visit.visit_id} ({self.image_type})"
