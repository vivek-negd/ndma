from django.db import models
from django.conf import settings
from .state import State
from .district import District
from .organization import Organization


class BulkUploadSession(models.Model):
    """Track each bulk upload session - when, who, where, how many"""
    
    # UPLOAD METADATA
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='bulk_upload_sessions'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)  # When upload happened
    
    # LOCATION & ORGANIZATION (scope of this upload)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True)
    
    # UPLOAD STATISTICS
    volunteers_created = models.IntegerField(default=0)  # How many volunteers from this upload
    total_rows_in_file = models.IntegerField(default=0)  # Total rows in uploaded file
    error_count = models.IntegerField(default=0)  # How many rows had errors
    
    # STATUS
    STATUS_CHOICES = [
        ('success', 'All rows processed successfully'),
        ('partial', 'Some rows had errors'),
        ('failed', 'Upload failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='success')
    
    # ADDITIONAL INFO
    file_name = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)  # Any notes about the upload
    
    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['state', 'district', 'uploaded_at']),
            models.Index(fields=['organization', 'uploaded_at']),
            models.Index(fields=['uploaded_by', 'uploaded_at']),
        ]
    
    def __str__(self):
        org_name = self.organization.name if self.organization else "No Org"
        return f"Upload by {self.uploaded_by.name} to {org_name} on {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
