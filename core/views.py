from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from django.db import connection as db_connection
from django.core.cache import cache
import os
import psutil
import time
import requests
from django.conf import settings

class HealthViewSet(viewsets.ViewSet):
    """
    ViewSet for monitoring system health and connections.
    Includes DB, Redis, and external service checks.
    """
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['get'])
    def status(self, request):
        """
        Comprehensive system health report
        """
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
        
        # Determine overall status
        failed_services = [s for s, v in data["services"].items() if v["status"] != "healthy"]
        data["overall_status"] = "unhealthy" if failed_services else "healthy"
        
        return Response(data)

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
        """Check 1C SOAP and other external dependencies"""
        results = {}
        
        # 1C Integration check (if URL available)
        soap_url = os.environ.get('SOAP_URL', '')
        if soap_url:
            try:
                # Basic ping/head request
                start = time.time()
                res = requests.head(soap_url, timeout=5)
                duration = (time.time() - start) * 1000
                results["1c_integration"] = {
                    "status": "healthy" if res.status_code < 500 else "unhealthy",
                    "status_code": res.status_code,
                    "url": soap_url,
                    "latency_ms": round(duration, 2)
                }
            except Exception as e:
                results["1c_integration"] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "url": soap_url
                }
        else:
            results["1c_integration"] = {"status": "not_configured"}

        return results

    def _get_system_metrics(self):
        try:
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            return {
                "cpu_percent": psutil.cpu_percent(interval=None),
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
                "uptime_seconds": int(time.time() - psutil.boot_time())
            }
        except:
            return {"status": "unavailable"}
