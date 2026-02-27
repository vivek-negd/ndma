from django.db import models
from .state import State
from .district import District
from .organization import Organization


class Volunteer(models.Model):

    GENDER_CHOICES = [
        (1, "Male"),
        (2, "Female"),
        (3, "Other"),
    ]

    BLOODGROUP_CHOICES = [
        (1, "A+"),
        (2, "A-"),
        (3, "B+"),
        (4, "B-"),
        (5, "O+"),
        (6, "O-"),
        (7, "AB+"),
        (8, "AB-"),
    ]

    mis_id = models.IntegerField(unique=True)

    name = models.CharField(max_length=100)

    gender_id = models.IntegerField(
        choices=GENDER_CHOICES,
        null=True,
        blank=True
    )

    bloodgroup_id = models.IntegerField(
        choices=BLOODGROUP_CHOICES,
        null=True,
        blank=True
    )

    dob = models.DateField(null=True, blank=True)

    aadhar = models.CharField(
        max_length=12,
        unique=True,
        null=True,
        blank=True
    )

    mobile = models.CharField(max_length=10, null=True, blank=True)

    email = models.EmailField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    mybharat_id = models.CharField(max_length=50, null=True, blank=True)

    # ✅ Proper Foreign Keys

    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="volunteers"
    )

    state = models.ForeignKey(
        State,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="volunteers"
    )

    district = models.ForeignKey(
        District,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="volunteers"
    )

    # Address
    postal_code = models.CharField(max_length=6, null=True, blank=True)
    town = models.CharField(max_length=100, null=True, blank=True)
    village = models.CharField(max_length=100, null=True, blank=True)
    full_address = models.TextField(null=True, blank=True)

    # Documents
    id_card = models.CharField(max_length=255, null=True, blank=True)
    certificate = models.CharField(max_length=255, null=True, blank=True)
    photo = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "models_volunteer"

    def __str__(self):
        return f"{self.name} ({self.mis_id})"