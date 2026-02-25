from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager
from .roles import UserRole


class User(AbstractBaseUser, PermissionsMixin):

    email_address = models.EmailField(unique=True)

    user_role = models.CharField(
        max_length=30,
        choices=UserRole.choices
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