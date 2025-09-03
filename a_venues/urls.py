from django.contrib import admin
from django.urls import include, path
from a_venues.views import home_page, create_venue, delete_venue, update_venue

urlpatterns = [
    path('', home_page, name='venue-home'),
    path('create-venue', create_venue, name='create_venue'),
    path('<int:pk>/delete/', delete_venue, name='venue_delete'),
    path('<int:pk>/update/', update_venue, name='update_venue'),
]



