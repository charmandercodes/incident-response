from django.urls import path
from . import views

urlpatterns = [
    # your existing patterns...
    path('logs/', views.logs_view, name='logs'),
]