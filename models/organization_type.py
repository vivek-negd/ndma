from django.db import models


class OrganizationType(models.Model):
    """Master table for organization types - allows future management"""
    
    code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "organization_types"
        ordering = ['code']
        verbose_name = "Organization Type"
        verbose_name_plural = "Organization Types"
    
    def __str__(self):
        return f"{self.code} - {self.name}"
