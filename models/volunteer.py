from django.db import models
from .state import State
from .district import District
from .organization import Organization


class Volunteer(models.Model):

    SALUTATION_CHOICES = [
        (1, "Mr."),
        (2, "Mrs."),
        (3, "Ms."),
        (4, "Dr."),
        (5, "Prof."),
    ]

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

    MARITALSTATUS_CHOICES = [
        (1, "Single"),
        (2, "Married"),
        (3, "Divorced"),
        (4, "Widowed"),
        (5, "Separated"),
    ]

    EDUCATION_CHOICES = [
        (1, "Below 10th"),
        (2, "10th Pass"),
        (3, "12th Pass"),
        (4, "Diploma"),
        (5, "Bachelor"),
        (6, "Master"),
        (7, "PhD"),
        (8, "Other"),
    ]

    SKILL_CHOICES = [
        (1, "First Aid"),
        (2, "Disaster Management"),
        (3, "Rescue Operations"),
        (4, "Community Care"),
        (5, "Training"),
        (6, "Other"),
    ]

    AREA_TYPE_CHOICES = [
        (1, "Urban"),
        (2, "Rural"),
        (3, "Semi-Urban"),
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

    salutation_id = models.IntegerField(
        choices=SALUTATION_CHOICES,
        null=True,
        blank=True
    )

    maritalstatus_id = models.IntegerField(
        choices=MARITALSTATUS_CHOICES,
        null=True,
        blank=True
    )

    emergency_contact = models.CharField(max_length=10, null=True, blank=True)

    education_id = models.IntegerField(
        choices=EDUCATION_CHOICES,
        null=True,
        blank=True
    )

    education_field = models.CharField(max_length=100, null=True, blank=True)

    skill_id = models.IntegerField(
        choices=SKILL_CHOICES,
        null=True,
        blank=True
    )

    area_type_id = models.IntegerField(
        choices=AREA_TYPE_CHOICES,
        null=True,
        blank=True
    )

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