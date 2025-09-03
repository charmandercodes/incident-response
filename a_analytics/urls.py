from django.urls import include, path
from .views import dashboard_view

urlpatterns = [
    path('', dashboard_view, name='analytics'),
]