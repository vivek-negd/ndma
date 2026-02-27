from django.db import models
from django.conf import settings
from core.base_model import BaseModel


class Permission(BaseModel):
    """Permission model - granular access control"""
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    module = models.CharField(max_length=100)
    action = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'permissions'
        ordering = ['module', 'action']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Role(BaseModel):
    """Role model - NDMA RBAC roles"""
    ROLE_CHOICES = (
        ('SUPER_ADMIN', 'Super Admin'),
        ('TECHNICAL_ADMIN', 'Technical Admin'),
        ('NDMA_ADMIN', 'NDMA Admin'),
        ('SDMA_ADMIN', 'SDMA Admin'),
        ('DDMA_NODAL_OFFICER', 'DDMA Nodal Officer'),
        ('TRAINING_INSTITUTE', 'Training Institute'),
        ('YOUTH_ORG_ADMIN', 'Youth Organisation Admin'),
        ('VOLUNTEER', 'Volunteer'),
        ('PUBLIC_USER', 'Public User'),
    )
    
    name = models.CharField(max_length=100, choices=ROLE_CHOICES, unique=True)
    description = models.TextField()
    permissions = models.ManyToManyField(Permission, blank=True, related_name='roles')
    is_active = models.BooleanField(default=True)
    hierarchy_level = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'roles'
        ordering = ['hierarchy_level']
    
    def __str__(self):
        return self.get_name_display()
    
    def has_permission(self, permission_code):
        return self.permissions.filter(code=permission_code).exists()
    
    def get_all_permissions(self):
        return list(self.permissions.values_list('code', flat=True))


class UserRole(BaseModel):
    """User-Role mapping with additional metadata"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name='users')
    
    state = models.CharField(max_length=100, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    organization = models.CharField(max_length=255, null=True, blank=True)
    designation = models.CharField(max_length=255, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_mfa_enabled = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'user_roles'
        unique_together = ('user', 'role')
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.role.get_name_display()}"
    
    def has_permission(self, permission_code):
        return self.role.has_permission(permission_code)
    
    def get_all_permissions(self):
        return self.role.get_all_permissions()


class RolePermissionAudit(BaseModel):
    """Audit trail for role and permission changes"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='permission_audits')
    action = models.CharField(max_length=50)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    permission = models.ForeignKey(Permission, on_delete=models.SET_NULL, null=True, blank=True)
    target_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='role_changes')
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        db_table = 'role_permission_audits'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.action} - {self.target_user} - {self.created_at}"