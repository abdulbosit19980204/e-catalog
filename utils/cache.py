from django.core.cache import caches, cache
import logging

logger = logging.getLogger(__name__)

def smart_cache_get(key, default=None):
    """
    Redis dan ma'lumot olishga harakat qiladi, agar Redis o'chiq bo'lsa 
    LocMem (fallback) dan qidiradi.
    """
    try:
        # Default (Redis) dan olishga harakat
        value = cache.get(key)
        if value is not None:
            return value
    except Exception as e:
        logger.warning(f"Primary cache (Redis) error: {e}")
    
    # Fallback (LocMem) dan ko'rish
    try:
        return caches['fallback'].get(key, default)
    except Exception as e:
        logger.error(f"Fallback cache error: {e}")
        return default

def smart_cache_set(key, value, timeout=300):
    """
    Redis va LocMem ikkalasiga ham yozadi.
    """
    # Redis ga yozish
    try:
        cache.set(key, value, timeout)
    except Exception as e:
        logger.warning(f"Primary cache (Redis) write error: {e}")
    
    # LocMem ga ham zaxira sifatida yozish
    try:
        caches['fallback'].set(key, value, timeout)
    except Exception as e:
        logger.error(f"Fallback cache write error: {e}")

def smart_cache_delete(key):
    """
    Har ikkala keshdan o'chiradi.
    """
    try:
        cache.delete(key)
    except Exception:
        pass
    
    try:
        caches['fallback'].delete(key)
    except Exception:
        pass
