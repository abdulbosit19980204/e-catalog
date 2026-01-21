from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Visit, VisitStepResult
from references.models import VisitStep

@receiver(post_save, sender=Visit)
def create_visit_steps(sender, instance, created, **kwargs):
    """
    Automatically create VisitStepResult items when a new Visit is created.
    Determines steps based on the visit's Project (or global steps if project is None).
    """
    if created:
        # Fetch relevant steps:
        # 1. Global steps (project is None)
        # 2. Project-specific steps (project matches visit's project)
        # We use Q objects to combine these conditions efficiently if we wanted to mix them,
        # but typically it's specific OR global. 
        # Here we'll take both (global + project specific) 
        from django.db.models import Q
        
        query = Q(project__isnull=True)
        if instance.project:
            query |= Q(project=instance.project)
        
        # Add Visit Type filter:
        # Step Applies IF: step.visit_type IS NULL OR step.visit_type == instance.visit_type
        type_query = Q(visit_type__isnull=True)
        if instance.visit_type:
            type_query |= Q(visit_type=instance.visit_type)
            
        steps = VisitStep.objects.filter(query).filter(type_query)
        
        # Prepare bulk creation
        results_to_create = []
        for step in steps:
            results_to_create.append(
                VisitStepResult(
                    visit=instance,
                    step=step,
                    is_completed=False
                )
            )
            
        if results_to_create:
            VisitStepResult.objects.bulk_create(results_to_create)
