"""
Database Lock Retry Middleware

Automatically retries database operations when SQLite reports "database is locked".
This improves user experience by handling transient lock contention transparently.
"""
import time
import random
import logging
from django.db import OperationalError
from django.http import HttpResponse

logger = logging.getLogger(__name__)


class DatabaseRetryMiddleware:
    """
    Middleware to automatically retry requests that fail due to database locks.
    
    This is especially important for SQLite in concurrent scenarios where:
    - Background sync tasks are writing to database
    - Admin users are editing records
    - API requests are being processed
    
    The middleware will retry up to max_retries times with exponential backoff.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.max_retries = 5
        
    def __call__(self, request):
        retries = 0
        
        while retries < self.max_retries:
            try:
                response = self.get_response(request)
                return response
                
            except OperationalError as e:
                if "database is locked" in str(e).lower() and retries < self.max_retries - 1:
                    # Exponential backoff with jitter
                    wait_time = random.uniform(0.1, 0.3) * (2 ** retries)
                    logger.warning(
                        f"Database locked for {request.path} - retrying in {wait_time:.2f}s "
                        f"(attempt {retries + 1}/{self.max_retries})"
                    )
                    time.sleep(wait_time)
                    retries += 1
                    continue
                else:
                    # Max retries exceeded or different error
                    logger.error(f"Database error after {retries + 1} retries: {e}")
                    raise
                    
        # Should never reach here, but just in case
        return HttpResponse("Service temporarily unavailable. Please try again.", status=503)
