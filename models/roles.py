from django.db import models


class UserRole(models.TextChoices):

    SUPER_ADMIN = "SUPER_ADMIN", "Super Admin"

    NATIONAL_ADMIN = "NATIONAL_ADMIN", "National Admin (NDMA)"

    STATE_ADMIN = "STATE_ADMIN", "State Admin (SDMA)"

    DISTRICT_ADMIN = "DISTRICT_ADMIN", "District Admin (DDMA)"

    BLOCK_ADMIN = "BLOCK_ADMIN", "Block Admin"

    VOLUNTEER = "VOLUNTEER", "Volunteer"