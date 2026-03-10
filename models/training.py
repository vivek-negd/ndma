from django.db import models
from .state import State
from .district import District
from .organization import Organization
from .user import User


class TrainingSchedule(models.Model):
    ORGANIZATION_TYPES = [
        ("NCC", "NCC"),
        ("NSS", "NSS"),
        ("YOUTH_ORG", "Youth Organisation"),
        ("INSTITUTE", "Institute"),
        ("OTHER", "Other"),
    ]

    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("APPROVED", "Approved"),
        ("PUBLISHED", "Published"),
    ]

    state = models.ForeignKey(State, on_delete=models.PROTECT, related_name="training_schedules")
    district = models.ForeignKey(District, on_delete=models.PROTECT, related_name="training_schedules", null=True, blank=True)

    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True)
    organization_name = models.CharField(max_length=200, null=True, blank=True)
    organization_type = models.CharField(max_length=30, choices=ORGANIZATION_TYPES, default="OTHER")

    number_of_volunteers = models.PositiveIntegerField(default=0)
    batch_no = models.CharField(max_length=50, unique=True, db_index=True, help_text="Batch identifier (e.g., FEB2026-MH-MUM-001)")
    institute_details = models.TextField(null=True, blank=True)
    trainers_details = models.TextField(null=True, blank=True)

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_training_schedules")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT")

    upload_option = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "models_training_schedule"
        indexes = [
            models.Index(fields=['batch_no']),
            models.Index(fields=['state', 'district']),
            models.Index(fields=['created_at']),
        ]
        unique_together = [['batch_no']]

    def __str__(self):
        return f"TrainingSchedule {self.id} - {self.organization_name or (self.organization.name if self.organization else 'N/A')}"


class TrainingSession(models.Model):
    schedule = models.ForeignKey(TrainingSchedule, on_delete=models.CASCADE, related_name="sessions")
    day_label = models.CharField(max_length=50)
    date = models.DateField(null=True, blank=True)
    upload_option = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "models_training_session"

    def __str__(self):
        return f"Session {self.day_label} for schedule {self.schedule_id}"
