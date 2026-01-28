from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UserBaseModel(models.Model):
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class AuthProject(UserBaseModel):
    name = models.CharField(max_length=255, help_text="Project nomi (masalan: Evyap)")
    project_code = models.CharField(max_length=100, unique=True, db_index=True, help_text="Unikal project kodi (clientdan keladi)")
    wsdl_url = models.URLField(help_text="Asosiy 1C WSDL URL manzili")
    wsdl_url_alt = models.URLField(blank=True, null=True, help_text="Muqobil (alternative) 1C WSDL URL manzili")
    service_url = models.URLField(blank=True, null=True, help_text="Service URL (agar WSDL dan farq qilsa)")
    
    def __str__(self):
        return f"{self.name} ({self.project_code})"

    class Meta:
        verbose_name = "Auth Project"
        verbose_name_plural = "Auth Projects"
        db_table = 'auth_project'

class UserProfile(UserBaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    project = models.ForeignKey('users.AuthProject', on_delete=models.SET_NULL, null=True, blank=True, related_name='user_profiles')
    code_1c = models.CharField(max_length=100, blank=True, null=True, db_index=True, help_text="1C dagi user kodi")
    code_project = models.CharField(max_length=100, blank=True, null=True, help_text="1C CodeProject")
    code_sklad = models.CharField(max_length=100, blank=True, null=True, help_text="1C CodeSklad")
    type_1c = models.CharField(max_length=50, blank=True, null=True, help_text="1C Type")
    business_region_code = models.CharField(max_length=100, blank=True, null=True, db_index=True, help_text="Business Region Code (1C)")
    business_region_name = models.CharField(max_length=255, blank=True, null=True, help_text="Business Region Name (1C)")
    
    def __str__(self):
        return f"{self.user.username} - {self.code_1c}"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        db_table = 'user_profile'

class AgentBusinessRegion(UserBaseModel):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='business_regions')
    code = models.CharField(max_length=100, db_index=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.profile.user.username} - {self.name} ({self.code})"

    class Meta:
        verbose_name = "Agent Business Region"
        verbose_name_plural = "Agent Business Regions"
        db_table = 'agent_business_region'
        unique_together = ('profile', 'code')

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)
