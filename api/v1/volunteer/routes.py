from django.urls import path
from .views import VolunteerCreateAPIView, VolunteerBulkUploadAPIView

urlpatterns = [
    path("create/", VolunteerCreateAPIView.as_view()),
    path("bulk-upload/", VolunteerBulkUploadAPIView.as_view()),
]