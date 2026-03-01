from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from .managers import UserManager

# Role choices for User model
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


class User(AbstractBaseUser, PermissionsMixin):

    email_address = models.EmailField(unique=True)

    # Profile fields requested by government onboarding
    name = models.CharField(max_length=255, null=True, blank=True)

    mobile = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        validators=[RegexValidator(r'^\d{10}$', 'Enter a 10 digit mobile number')]
    )

    designation = models.CharField(max_length=255, null=True, blank=True)

    aadhar = models.CharField(
        max_length=12,
        null=True,
        blank=True,
        validators=[RegexValidator(r'^\d{12}$', 'Enter a 12 digit Aadhar number')]
    )

    user_role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES
    )

    # Hierarchical Mapping (MANDATORY for RBAC)
    state_code = models.CharField(max_length=10, null=True, blank=True)
    district_code = models.CharField(max_length=10, null=True, blank=True)
    block_code = models.CharField(max_length=10, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email_address"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email_address} ({self.user_role})"

    def get_effective_permissions(self):
        """Union of active role permissions and active per-user overrides"""
        from models.role import UserPermissionOverride  # local import to avoid cycles

        permission_codes = set()

        active_roles = self.user_roles.filter(is_active=True).select_related('role').prefetch_related('role__permissions')
        for user_role in active_roles:
            permission_codes.update(user_role.role.get_all_permissions())

        overrides = UserPermissionOverride.objects.filter(user=self, is_active=True).select_related('permission')
        for override in overrides:
            permission_codes.add(override.permission.code)

        return sorted(permission_codes)