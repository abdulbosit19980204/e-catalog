from django.shortcuts import render
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny
from .models import SystemSettings, AITokenUsage, AIModel
from django.db import connection as db_connection
from django.core.cache import cache
import os
try:
    import psutil
except ImportError:
    psutil = None
import time
import requests
from django.conf import settings

from drf_spectacular.utils import extend_schema, OpenApiResponse

from rest_framework.permissions import IsAdminUser, AllowAny

class HealthViewSet(viewsets.ViewSet):
    """
    ViewSet for monitoring system health and connections.
    Includes DB, Redis, and external service checks.
    """
    def get_permissions(self):
        if self.action == 'status':
            return [AllowAny()]
        return [IsAdminUser()]

    @extend_schema(
        responses={200: OpenApiResponse(description="System health data")},
        summary="Get system health status",
        description="Returns real-time status of database, redis, external services and system metrics."
    )
    @action(detail=False, methods=['get'])
    def status(self, request):
        """
        Comprehensive system health report
        """
        try:
            data = {
                "timestamp": time.time(),
                "services": {
                    "database": self._check_db(),
                    "redis": self._check_redis(),
                    "external": self._check_external_services(),
                },
                "system": self._get_system_metrics(),
                "environment": {
                    "debug": settings.DEBUG,
                    "timezone": settings.TIME_ZONE,
                    "allowed_hosts": settings.ALLOWED_HOSTS,
                }
            }
            
            # Determine overall status - flatten services to check all
            all_statuses = []
            for s_name, s_val in data["services"].items():
                if s_name == "external":
                    for ext_s in s_val.values():
                        if isinstance(ext_s, dict) and "status" in ext_s:
                            all_statuses.append(ext_s["status"])
                elif "status" in s_val:
                    all_statuses.append(s_val["status"])
            
            data["overall_status"] = "unhealthy" if any(s != "healthy" and s != "not_configured" for s in all_statuses) else "healthy"
            
            return Response(data)
        except Exception as e:
            import traceback
            print(f"ERROR in HealthViewSet.status: {e}")
            print(traceback.format_exc())
            return Response({"status": "error", "message": str(e)}, status=500)

    def _check_db(self):
        start = time.time()
        try:
            db_connection.ensure_connection()
            duration = (time.time() - start) * 1000
            return {
                "status": "healthy",
                "latency_ms": round(duration, 2),
                "engine": settings.DATABASES['default']['ENGINE'].split('.')[-1],
                "host": settings.DATABASES['default'].get('HOST', 'local')
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "latency_ms": round((time.time() - start) * 1000, 2)
            }

    def _check_redis(self):
        start = time.time()
        try:
            # Check if redis is responsive
            cache.set('health_check', 'ok', timeout=1)
            val = cache.get('health_check')
            duration = (time.time() - start) * 1000
            
            if val == 'ok':
                return {
                    "status": "healthy",
                    "latency_ms": round(duration, 2),
                    "url": os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1')
                }
            return {"status": "unhealthy", "error": "Redis did not return expected value"}
        except Exception as e:
            return {
                "status": "unhealthy", 
                "error": str(e),
                "latency_ms": round((time.time() - start) * 1000, 2)
            }

    def _check_external_services(self):
        """Check 1C SOAP and other external dependencies, including Project-specific URLs"""
        results = {}
        
        # 1. Base SOAP URL check
        soap_url = os.environ.get('SOAP_URL', '')
        if soap_url:
            results["main_soap_service"] = self._ping_url(soap_url, "Main 1C Service")
        
        # 2. Dynamic Auth Project URLs (WSDLs and Service URLs for agents)
        try:
            from users.models import AuthProject
            auth_projects = AuthProject.objects.filter(is_active=True).exclude(wsdl_url="")[:10]
            for ap in auth_projects:
                results[f"auth_{ap.project_code}_wsdl"] = self._ping_url(ap.wsdl_url, f"Auth WSDL (Main): {ap.name}")
                if ap.wsdl_url_alt:
                    results[f"auth_{ap.project_code}_wsdl_alt"] = self._ping_url(ap.wsdl_url_alt, f"Auth WSDL (Alt): {ap.name}")
                if ap.service_url:
                    results[f"auth_{ap.project_code}_service"] = self._ping_url(ap.service_url, f"Auth Service: {ap.name}")
        except Exception as e:
            results["auth_project_error"] = {"status": "error", "message": f"Auth projects check failed: {str(e)}"}
            
        return results

    def _ping_url(self, url, name):
        """Helper to ping an external URL and return status"""
        try:
            start = time.time()
            # Try HEAD first, then GET if HEAD fails (some servers block HEAD)
            try:
                res = requests.head(url, timeout=5)
                if res.status_code >= 400:
                   res = requests.get(url, timeout=5, stream=True)
            except:
                res = requests.get(url, timeout=5, stream=True)
                
            duration = (time.time() - start) * 1000
            return {
                "name": name,
                "status": "healthy" if res.status_code < 500 else "unhealthy",
                "status_code": res.status_code,
                "url": url,
                "latency_ms": round(duration, 2)
            }
        except Exception as e:
            return {
                "name": name,
                "status": "unhealthy",
                "error": str(e),
                "url": url
            }

    def _get_system_metrics(self):
        if not psutil:
            return {"status": "unavailable", "reason": "psutil not installed"}
        try:
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get top processes by CPU
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status']):
                try:
                    p_info = proc.info
                    # Skip idle/system processes with 0 usage to keep it clean if we want
                    processes.append({
                        "pid": p_info['pid'],
                        "name": p_info['name'],
                        "cpu": p_info['cpu_percent'],
                        "memory_mb": round(p_info['memory_info'].rss / (1024 * 1024), 2),
                        "status": p_info['status']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            # Sort by CPU and take top 10
            top_cpu = sorted(processes, key=lambda x: x['cpu'], reverse=True)[:10]
            # Sort by Memory and take top 10
            top_mem = sorted(processes, key=lambda x: x['memory_mb'], reverse=True)[:10]

            return {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory": {
                    "total_gb": round(mem.total / (1024**3), 2),
                    "used_gb": round(mem.used / (1024**3), 2),
                    "percent": mem.percent
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "percent": disk.percent
                },
                "uptime_seconds": int(time.time() - psutil.boot_time()),
                "top_processes_cpu": top_cpu,
                "top_processes_mem": top_mem
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

class SystemSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSettings
        fields = ['id', 'key', 'value', 'description', 'is_secret', 'updated_at']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.is_secret:
            ret['value'] = "********"
        return ret

class SystemSettingsViewSet(viewsets.ModelViewSet):
    """ViewSet for managing dynamic system settings"""
    queryset = SystemSettings.objects.filter(is_deleted=False)
    serializer_class = SystemSettingsSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'key'
    lookup_value_regex = '[^/]+'

class AITokenUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AITokenUsage
        fields = '__all__'

class AITokenUsageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing AI token usage and statistics"""
    queryset = AITokenUsage.objects.all()
    serializer_class = AITokenUsageSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Returns aggregated token usage statistics"""
        from django.db.models import Sum, Count
        from django.db.models.functions import TruncDay
        
        # Total stats
        totals = AITokenUsage.objects.aggregate(
            total_requests=Count('id'),
            total_input=Sum('input_tokens'),
            total_output=Sum('output_tokens'),
            total_all=Sum('total_tokens')
        )
        
        # Stats per model
        model_stats = AITokenUsage.objects.values('model_name').annotate(
            requests=Count('id'),
            tokens=Sum('total_tokens')
        ).order_by('-tokens')
        
        # Daily usage (last 30 days)
        daily_usage = AITokenUsage.objects.annotate(
            day=TruncDay('created_at')
        ).values('day').annotate(
            tokens=Sum('total_tokens'),
            requests=Count('id')
        ).order_by('-day')[:30]
        
        return Response({
            "totals": totals,
            "models": model_stats,
            "daily": daily_usage
        })

class AIModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIModel
        fields = '__all__'

class AIModelViewSet(viewsets.ModelViewSet):
    """ViewSet for managing AI Models"""
    queryset = AIModel.objects.filter(is_deleted=False)
    serializer_class = AIModelSerializer
    permission_classes = [IsAdminUser]
