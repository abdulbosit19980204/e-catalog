import traceback
import json
from django.utils.deprecation import MiddlewareMixin
from core.models import ErrorLog

class ExceptionLoggingMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        try:
            # Extract request data
            request_data = None
            if request.method in ['POST', 'PUT', 'PATCH']:
                try:
                    request_data = json.dumps(request.data) if hasattr(request, 'data') else str(request.body)
                except Exception:
                    request_data = "Could not parse request body"

            # Create ErrorLog
            ErrorLog.objects.create(
                error_type=type(exception).__name__,
                message=str(exception),
                stack_trace=traceback.format_exc(),
                path=request.path,
                method=request.method,
                query_params=dict(request.GET.items()),
                request_data=request_data,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                ip_address=request.META.get('REMOTE_ADDR', ''),
                user=request.user if request.user.is_authenticated else None
            )
        except Exception as e:
            # If logging itself fails, print to console but don't crash
            print(f"CRITICAL: ExceptionLoggingMiddleware failed: {e}")
        
        return None # Let other middlewares handle the exception (e.g. DRF default handler)
