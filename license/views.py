from rest_framework import viewsets, status, views
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .models import AppLicense, AppVersionMetadata, AccessHistory
from .serializers import AppLicenseSerializer, AppVersionMetadataSerializer, AccessHistorySerializer

@extend_schema(tags=['License Management'])
class LicenseStatusView(views.APIView):
    """
    Mobile License Status Check
    
    This endpoint allows mobile applications to verify their license status,
    check for updates, and log access history.
    """
    
    @extend_schema(
        summary="Check Mobile License Status",
        description="Verify if a mobile app license is active and get version information",
        parameters=[
            OpenApiParameter(
                name='X-License-Key',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                required=True,
                description='Unique license key assigned to the mobile user/organization'
            ),
            OpenApiParameter(
                name='X-App-Version',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                required=False,
                description='Current app version (e.g., 1.0.4) for logging purposes'
            ),
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "can_access": {"type": "boolean"},
                    "license_info": {"type": "object"},
                    "version_info": {"type": "object"}
                }
            },
            400: {"description": "Missing X-License-Key header"},
            404: {"description": "License not found"}
        },
        examples=[
            OpenApiExample(
                'Success Response',
                value={
                    "can_access": True,
                    "license_info": {
                        "license_key": "MOBILE-USER-001",
                        "status": "ACTIVE",
                        "starts_at": "2026-01-30T00:00:00Z",
                        "expires_at": "2026-03-01T00:00:00Z",
                        "is_unlimited": False,
                        "days_remaining": 30
                    },
                    "version_info": {
                        "latest": "1.0.5",
                        "is_update_required": False
                    }
                },
                response_only=True,
            ),
        ]
    )
    def get(self, request):
        license_key = request.headers.get('X-License-Key')
        app_version = request.headers.get('X-App-Version')
        
        if not license_key:
            return Response({"error": "X-License-Key header is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        license = AppLicense.objects.filter(license_key=license_key).first()
        if not license:
            return Response({"can_access": False, "reason": "License not found"}, status=status.HTTP_404_NOT_FOUND)
            
        # Check expiry
        can_access = license.status == 'ACTIVE'
        if not license.is_unlimited and license.expires_at and license.expires_at < timezone.now():
            can_access = False
            license.status = 'EXPIRED'
            license.save()

        # Get version info
        latest_version = AppVersionMetadata.objects.order_by('-release_date').first()
        
        # Log access if app_version provided
        if app_version:
            AccessHistory.objects.create(
                license=license,
                version=app_version,
                ip_address=self.get_client_ip(request),
                device_info={"user_agent": request.META.get('HTTP_USER_AGENT', '')}
            )

        return Response({
            "can_access": can_access,
            "license_info": AppLicenseSerializer(license).data,
            "version_info": {
                "latest": latest_version.version_code if latest_version else None,
                "is_update_required": latest_version.is_mandatory_update if latest_version else False
            }
        })

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

@extend_schema(tags=['License Management'])
class AccessHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View access history logs for mobile app check-ins
    """
    queryset = AccessHistory.objects.all().order_by('-accessed_at')
    serializer_class = AccessHistorySerializer
    filterset_fields = ['license__license_key', 'version']
