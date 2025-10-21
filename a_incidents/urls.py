from django.urls import path
from a_incidents.views import (
    home_page,
    create_incident,
    delete_incident,
    update_incident,
)

urlpatterns = [
    path("", home_page, name="home"),
    path("create-incident/", create_incident, name="create_incident"),
    path("delete/<int:pk>/", delete_incident, name="incident_delete"),
    path("update/<int:pk>/", update_incident, name="update_incident"),
]
