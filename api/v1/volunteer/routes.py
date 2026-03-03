from django.urls import path
from .views import VolunteerCreateAPIView, VolunteerBulkUploadAPIView, OrganizationCoverageAPIView, VolunteerChoicesAPIView

urlpatterns = [
    path("choices/", VolunteerChoicesAPIView.as_view()),
    path("create/", VolunteerCreateAPIView.as_view()),
    path("bulk-upload/", VolunteerBulkUploadAPIView.as_view()),
    path("coverage/", OrganizationCoverageAPIView.as_view()),
]