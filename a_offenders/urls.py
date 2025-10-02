from django.urls import path
from .views import create_offender, update_offender, delete_offender, offender_page, offender_detail, offenders_csv
from django.views.generic import RedirectView  # add this

urlpatterns = [
    path("", offender_page, name="offender-home"),
    path("create/", create_offender, name="create-offender"),
    # --- TEMP alias so /offenders/create-offender redirects correctly ---
    path(
        "create-offender",
        RedirectView.as_view(pattern_name="create-offender", permanent=False),
    ),
    # (you can alternatively just serve the same view:)
    # path("create-offender", create_offender),

    path("<int:pk>/", offender_detail, name="offender-detail"),
    path("<int:pk>/update/", update_offender, name="update-offender"),
    path("<int:pk>/delete/", delete_offender, name="delete-offender"),
    path("export.csv", offenders_csv, name="offenders-csv"),
]
