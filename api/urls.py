from django.urls import path
from rest_framework.routers import DefaultRouter
from nomenklatura.views import NomenklaturaViewSet, NomenklaturaImageViewSet
from client.views import ClientViewSet, ClientImageViewSet
from .views import (
    ProjectViewSet,
    ProjectImageViewSet,
    ImageStatusViewSet,
    ImageSourceViewSet,
    ThumbnailFeedView,
    ProjectThumbnailView,
    ClientThumbnailView,
    NomenklaturaThumbnailView,
)

router = DefaultRouter()
router.register('nomenklatura', NomenklaturaViewSet)
router.register('nomenklatura-image', NomenklaturaImageViewSet)
router.register('client', ClientViewSet)
router.register('client-image', ClientImageViewSet)
router.register('project', ProjectViewSet)
router.register('project-image', ProjectImageViewSet)
router.register('image-status', ImageStatusViewSet)
router.register('image-source', ImageSourceViewSet)

urlpatterns = [
    path('thumbnails/', ThumbnailFeedView.as_view(), name='thumbnail-feed'),
    path('thumbnails/projects/', ProjectThumbnailView.as_view(), name='project-thumbnail-feed'),
    path('thumbnails/clients/', ClientThumbnailView.as_view(), name='client-thumbnail-feed'),
    path('thumbnails/nomenklatura/', NomenklaturaThumbnailView.as_view(), name='nomenklatura-thumbnail-feed'),
]

urlpatterns += router.urls
