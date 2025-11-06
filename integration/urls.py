from django.urls import path
from . import views

app_name = 'integration'

urlpatterns = [
    path('sync/nomenklatura/<int:integration_id>/', views.sync_nomenklatura_from_1c, name='sync_nomenklatura'),
    path('sync/clients/<int:integration_id>/', views.sync_clients_from_1c, name='sync_clients'),
    path('sync/status/<str:task_id>/', views.get_sync_status, name='sync_status'),
]

