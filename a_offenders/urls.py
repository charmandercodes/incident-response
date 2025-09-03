from django.urls import include, path
from a_offenders.views import create_offender, delete_offender,  update_offender, offender_page

urlpatterns = [
    path('', offender_page, name='offender-home'),
    path('create-offender', create_offender, name='create-offender'),
    path('<int:pk>/delete/', delete_offender, name='delete-offender'),
    path('<int:pk>/update/', update_offender, name='update-offender'),
]



