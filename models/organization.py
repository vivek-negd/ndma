from django.db import models
from .state import State
from .district import District
from .organization_type import OrganizationType


class Organization(models.Model):
    
    name = models.CharField(max_length=100)
    org_type = models.ForeignKey(
        OrganizationType,
        on_delete=models.PROTECT,
        related_name='organizations'
    )
    
    # Geographic scope
    state = models.ForeignKey(State, on_delete=models.PROTECT, related_name='organizations')
    district = models.ForeignKey(District, on_delete=models.PROTECT, related_name='organizations')
    
    # Contact info
    contact_person = models.CharField(max_length=100, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True, null=True)
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "models_organization"
        unique_together = [['name', 'state', 'district']]
        ordering = ['org_type', 'name']

    def __str__(self):
        return f"{self.name} ({self.org_type}) - {self.district.name}"
    
    @property
    def volunteer_count(self):
        return self.volunteers.count()