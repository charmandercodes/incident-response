from django.urls import path
from .views import (
    offender_page, create_offender, update_offender, delete_offender,
    offender_detail, offenders_csv
)

urlpatterns = [
    path("", offender_page, name="offender-home"),
    path("create/", create_offender, name="create-offender"),
    path("<int:pk>/", offender_detail, name="offender-detail"),
    path("<int:pk>/update/", update_offender, name="update-offender"),
    path("<int:pk>/delete/", delete_offender, name="delete-offender"),
    path("export.csv", offenders_csv, name="offenders-csv"),
]
