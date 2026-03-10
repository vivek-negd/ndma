from django.urls import path
from .views import VolunteerCreateAPIView, VolunteerBulkUploadAPIView, OrganizationCoverageAPIView, VolunteerChoicesAPIView, VolunteerExportAPIView, VolunteerCoverageReportAPIView
from models.volunteer import Volunteer
from models.organization import Organization

urlpatterns = [
    path("choices/", VolunteerChoicesAPIView.as_view()),
    path("create/", VolunteerCreateAPIView.as_view()),
    path("bulk-upload/", VolunteerBulkUploadAPIView.as_view()),
    path("coverage/", OrganizationCoverageAPIView.as_view()),
    path("coverage-report/", VolunteerCoverageReportAPIView.as_view()),
    path("export/", VolunteerExportAPIView.as_view()),
]

# confirm these rows exist and have null org
Volunteer.objects.filter(organization__isnull=True, deleted_at__isnull=True).count()
list(Volunteer.objects.filter(organization__isnull=True).values('id','mis_id','name','state_id','district_id')[:50])

# confirm organization id 4 exists (example)
Organization.objects.filter(id=4).values('id','name').first()