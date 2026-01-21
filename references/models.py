from django.db import models
from api.models import BaseModel

class VisitType(BaseModel):
    """Dynamic Visit Types"""
    code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    sort_order = models.IntegerField(default=0)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Visit Type"
        verbose_name_plural = "Visit Types"
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class VisitStatus(BaseModel):
    """Dynamic Visit Statuses"""
    code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=20, default='#000000', help_text="Hex color code")
    sort_order = models.IntegerField(default=0)
    is_final = models.BooleanField(default=False, help_text="If true, visit is considered closed")

    class Meta:
        verbose_name = "Visit Status"
        verbose_name_plural = "Visit Statuses"
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class VisitPriority(BaseModel):
    """Dynamic Visit Priorities"""
    code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    level = models.IntegerField(default=1, help_text="Higher number = higher priority")
    color = models.CharField(max_length=20, default='#000000')

    class Meta:
        verbose_name = "Visit Priority"
        verbose_name_plural = "Visit Priorities"
        ordering = ['-level', 'name']

    def __str__(self):
        return self.name


class VisitStep(BaseModel):
    """Dynamic Visit Steps (Tasks to be done during a visit)"""
    project = models.ForeignKey('users.AuthProject', on_delete=models.CASCADE, related_name='visit_steps', null=True, blank=True)
    visit_type = models.ForeignKey('VisitType', on_delete=models.SET_NULL, related_name='steps', null=True, blank=True, help_text="Specific visit type (optional)")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    input_type = models.CharField(
        max_length=50, 
        choices=[
            ('text', 'Text Input'),
            ('number', 'Number Input'),
            ('checkbox', 'Checkbox'),
            ('photo', 'Photo'),
            ('select', 'Selection'),
        ],
        default='checkbox'
    )
    is_required = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Visit Step"
        verbose_name_plural = "Visit Steps"
        ordering = ['sort_order']

    def __str__(self):
        return self.title
