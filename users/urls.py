from django.urls import path
from .views import OneCLoginView

urlpatterns = [
    path('auth/1c-login/', OneCLoginView.as_view(), name='auth-1c-login'),
]
