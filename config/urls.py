"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from config.auth_views import APITokenObtainPairView, APITokenRefreshView, APITokenVerifyView
from config import admin_views

urlpatterns = [
    path('admin/import-export/', admin.site.admin_view(admin_views.import_export_dashboard), name='admin-import-export'),
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    
    # Authentication
    path('api/token/', APITokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', APITokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', APITokenVerifyView.as_view(), name='token_verify'),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Integration API
    # Integration API
    path('api/v1/integration/', include('integration.urls')),
    
    # Users & Auth API
    path('api/v1/', include('users.urls')),

    # Chat API
    path('api/v1/chat/', include('chat.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
