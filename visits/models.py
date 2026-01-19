"""
Visit Management Models
Enterprise-grade visit tracking system with extensible architecture
"""
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal

# Dynamic References
from references.models import VisitType, VisitStatus, VisitPriority, VisitStep


class BaseModel(models.Model):
    """Abstract base model with common fields"""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    
    class Meta:
        abstract = True


class Visit(BaseModel):
    """
    Core visit tracking model
    Now uses dynamic references for Type, Status, and Priority
    """
    # Project scoping
    project = models.ForeignKey(
        'users.AuthProject',
        on_delete=models.CASCADE,
        related_name='visits',
        null=True,
        blank=True,
        db_index=True
    )
    
    # Primary identification
    visit_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    
    # Agent information
    agent = models.ForeignKey(
        'users.UserProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='visits',
        db_index=True,
        help_text="Tashrifni amalga oshiradigan agent"
    )
    agent_code = models.CharField(max_length=50, db_index=True)
    agent_name = models.CharField(max_length=255)
    agent_phone = models.CharField(max_length=20, blank=True)
    
    # Client reference
    client = models.ForeignKey(
        'client.Client',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='visits',
        db_index=True,
        help_text="Tashrif buyuriladigan mijoz"
    )
    client_code = models.CharField(max_length=100, db_index=True)
    client_name = models.CharField(max_length=255)
    client_address = models.TextField(blank=True)
    
    # Dynamic Classification (Foreign Keys)
    # Note: We use related_name='+' for some to avoid clutter if not needed, 
    # but 'visits' is good for reverse lookup.
    visit_type = models.ForeignKey(
        VisitType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='visits',
        help_text="Tashrif turi (Dynamic)"
    )
    status = models.ForeignKey(
        VisitStatus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='visits',
        help_text="Tashrif holati (Dynamic)"
    )
    priority = models.ForeignKey(
        VisitPriority,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='visits',
        help_text="Prioritet (Dynamic)"
    )
    
    # Scheduling
    planned_date = models.DateField(db_index=True)
    planned_time = models.TimeField(null=True, blank=True)
    planned_duration_minutes = models.IntegerField(
        default=30,
        validators=[MinValueValidator(5), MaxValueValidator(480)]
    )
    
    # Actual timing (Requested Feature)
    actual_start_time = models.DateTimeField(null=True, blank=True, db_index=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True, help_text="Aniq davomiylik (calculated)")
    
    # Location tracking
    check_in_latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    check_in_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    check_in_address = models.TextField(blank=True)
    check_in_accuracy = models.FloatField(null=True, blank=True)
    
    check_out_latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    check_out_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    # Visit content
    purpose = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    # Outcomes
    outcome = models.TextField(blank=True)
    next_visit_date = models.DateField(null=True, blank=True)
    
    # Ratings
    client_satisfaction = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    agent_notes = models.TextField(blank=True)
    supervisor_notes = models.TextField(blank=True)
    
    # Metadata
    sync_status = models.CharField(
        max_length=20,
        choices=[('PENDING', 'Kutilmoqda'), ('SYNCED', 'Sinxronlangan'), ('FAILED', 'Xatolik')],
        default='PENDING',
        db_index=True
    )
    sync_error = models.TextField(blank=True)
    
    # Task Tracking
    tasks_planned = models.JSONField(default=list, blank=True, help_text="List of tasks planned for this visit")
    tasks_completed = models.JSONField(default=list, blank=True, help_text="List of tasks completed during this visit")
    
    # Outcomes
    next_visit_notes = models.TextField(blank=True, help_text="Notes for the next scheduled visit")

    
    # Metadata
    cancelled_reason = models.TextField(blank=True)
    cancelled_by = models.CharField(max_length=100, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'visits'
        ordering = ['-planned_date', '-planned_time']
        indexes = [
            models.Index(fields=['project', 'agent', 'planned_date', 'status']),
            models.Index(fields=['client', 'actual_start_time']),
            models.Index(fields=['visit_type', 'created_at']),
            models.Index(fields=['status', 'planned_date']),
        ]
        verbose_name = 'Visit'
        verbose_name_plural = 'Visits'
    
    def __str__(self):
        return f"{self.agent_name} -> {self.client_name} ({self.planned_date})"
    
    def check_in(self, latitude, longitude, accuracy=None):
        """Check in to visit location"""
        self.actual_start_time = timezone.now()
        self.check_in_latitude = Decimal(str(latitude))
        self.check_in_longitude = Decimal(str(longitude))
        self.check_in_accuracy = accuracy
        self.sync_status = 'PENDING'
        
        # Dynamic Status Update
        try:
            self.status = VisitStatus.objects.filter(code='IN_PROGRESS').first()
        except Exception:
            pass # Graceful failure if status not seeded
            
        self.save()
    
    def check_out(self, latitude=None, longitude=None):
        """Complete visit and calculate duration"""
        self.actual_end_time = timezone.now()
        if latitude and longitude:
            self.check_out_latitude = Decimal(str(latitude))
            self.check_out_longitude = Decimal(str(longitude))
        
        if self.actual_start_time:
            self.duration = self.actual_end_time - self.actual_start_time
            
        self.sync_status = 'PENDING'
        
        # Dynamic Status Update
        try:
            self.status = VisitStatus.objects.filter(code='COMPLETED').first()
        except Exception:
            pass

        self.save()
    
    def cancel(self, reason, cancelled_by):
        """Cancel scheduled visit"""
        self.cancelled_reason = reason
        self.cancelled_by = cancelled_by
        self.cancelled_at = timezone.now()
        self.sync_status = 'PENDING'
        
        # Dynamic Status Update
        try:
            self.status = VisitStatus.objects.filter(code='CANCELLED').first()
        except Exception:
            pass
            
        self.save()
    
    @property
    def is_overdue(self):
        """Check if visit is overdue"""
        if self.status and self.status.code in ['SCHEDULED', 'CONFIRMED']:
            return timezone.now().date() > self.planned_date
        return False
    
    @property
    def is_in_progress(self):
        """Check if visit is currently in progress"""
        return self.status and self.status.code == 'IN_PROGRESS'


class VisitStepResult(BaseModel):
    """
    Result of a specific step in a visit
    """
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name='step_results')
    step = models.ForeignKey(VisitStep, on_delete=models.CASCADE, related_name='results')
    
    value_text = models.TextField(blank=True, null=True)
    value_number = models.FloatField(blank=True, null=True)
    value_boolean = models.BooleanField(default=False)
    value_photo = models.ImageField(upload_to='visit_steps/', blank=True, null=True)
    
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['visit', 'step']
        ordering = ['step__sort_order']

    def __str__(self):
        return f"{self.visit} - {self.step.title}"


class VisitPlan(BaseModel):
    """
    Visit planning and scheduling
    """
    plan_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey('users.AuthProject', on_delete=models.CASCADE, related_name='visit_plans', null=True, blank=True)
    
    agent = models.ForeignKey('users.UserProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='visit_plans')
    agent_code = models.CharField(max_length=50, db_index=True)
    
    client = models.ForeignKey('client.Client', on_delete=models.SET_NULL, null=True, blank=True, related_name='visit_plans')
    client_code = models.CharField(max_length=100, db_index=True)
    
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
    
    planned_weekday = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(6)])
    planned_time = models.TimeField()
    duration_minutes = models.IntegerField(default=30)
    
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    priority = models.ForeignKey(VisitPriority, on_delete=models.SET_NULL, null=True, blank=True)
    
    auto_generate = models.BooleanField(default=True)
    generate_days_ahead = models.IntegerField(default=7)
    
    class Meta:
        db_table = 'visit_plans'
        ordering = ['agent_code', 'planned_weekday', 'planned_time']
        unique_together = [['project', 'agent_code', 'client_code', 'planned_weekday', 'planned_time']]
    
    def __str__(self):
        return f"{self.agent_code} -> {self.client_code}"


class VisitImage(BaseModel):
    """
    Images captured during visits
    """
    image_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name='images')
    
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
    
    captured_at = models.DateTimeField(auto_now_add=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    client_image_id = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'visit_images'
        ordering = ['-captured_at']
    
    def __str__(self):
        return f"Image for {self.visit.visit_id}"
