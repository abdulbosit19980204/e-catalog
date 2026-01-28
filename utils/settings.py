import os
from django.conf import settings
from core.models import SystemSettings
import logging

logger = logging.getLogger(__name__)

def get_system_setting(key, default=None):
    """
    Fetches a system setting from the database.
    Falls back to environment variables or django settings if not found.
    """
    try:
        setting = SystemSettings.objects.filter(key=key, is_active=True).first()
        if setting:
            return setting.value
    except Exception as e:
        logger.error(f"Error fetching system setting {key}: {str(e)}")

    # Fallback to environment variables
    env_val = os.environ.get(key)
    if env_val:
        return env_val

    # Fallback to Django settings
    return getattr(settings, key, default)
