from django.urls import path
from rest_framework.routers import DefaultRouter
from nomenklatura.views import NomenklaturaViewSet, NomenklaturaImageViewSet
from client.views import ClientViewSet, ClientImageViewSet, VisitImageViewSet
from .views import (
    ProjectViewSet,
    ProjectImageViewSet,
    ImageStatusViewSet,
    ImageSourceViewSet,
    ThumbnailFeedView,
    ProjectThumbnailView,
    ClientThumbnailView,
    NomenklaturaThumbnailView,
    AgentLocationViewSet,
    ClearDatabaseView,
)
from references.views import (
    VisitTypeViewSet, 
    VisitStatusViewSet, 
    VisitPriorityViewSet, 
    VisitStepViewSet
)

router = DefaultRouter()
router.register('visit-types', VisitTypeViewSet)
router.register('visit-statuses', VisitStatusViewSet)
router.register('visit-priorities', VisitPriorityViewSet)
router.register('visit-steps', VisitStepViewSet)

router.register('nomenklatura', NomenklaturaViewSet)
router.register('nomenklatura-image', NomenklaturaImageViewSet)
router.register('client', ClientViewSet)
router.register('client-image', ClientImageViewSet)
router.register('project', ProjectViewSet)
router.register('project-image', ProjectImageViewSet)
router.register('image-status', ImageStatusViewSet)
router.register('image-source', ImageSourceViewSet)
router.register('agent-location', AgentLocationViewSet)
router.register('visit-image', VisitImageViewSet, basename='visit-image')

urlpatterns = [
    path('thumbnails/', ThumbnailFeedView.as_view(), name='thumbnail-feed'),
    path('thumbnails/projects/', ProjectThumbnailView.as_view(), name='project-thumbnail-feed'),
    path('thumbnails/clients/', ClientThumbnailView.as_view(), name='client-thumbnail-feed'),
    path('thumbnails/nomenklatura/', NomenklaturaThumbnailView.as_view(), name='nomenklatura-thumbnail-feed'),
    path('admin/clear-db/', ClearDatabaseView.as_view(), name='clear-database'),
]

urlpatterns += router.urls
