from django.core.management.base import BaseCommand
from models.choices import (
    SalutationChoice,
    GenderChoice,
    BloodGroupChoice,
    MaritalStatusChoice,
    EducationChoice,
    SkillChoice,
    AreaTypeChoice,
)


class Command(BaseCommand):
    help = "Seed volunteer choice master tables"

    def handle(self, *args, **options):
        # Salutation Choices
        salutation_data = [
            (1, "Mr."),
            (2, "Mrs."),
            (3, "Ms."),
            (4, "Dr."),
            (5, "Prof."),
        ]
        for code, label in salutation_data:
            SalutationChoice.objects.get_or_create(
                code=code,
                defaults={"label": label, "is_active": True}
            )
            self.stdout.write(self.style.SUCCESS(f"✓ Salutation: {label}"))

        # Gender Choices
        gender_data = [
            (1, "Male"),
            (2, "Female"),
            (3, "Other"),
        ]
        for code, label in gender_data:
            GenderChoice.objects.get_or_create(
                code=code,
                defaults={"label": label, "is_active": True}
            )
            self.stdout.write(self.style.SUCCESS(f"✓ Gender: {label}"))

        # Blood Group Choices
        bloodgroup_data = [
            (1, "A+"),
            (2, "A-"),
            (3, "B+"),
            (4, "B-"),
            (5, "O+"),
            (6, "O-"),
            (7, "AB+"),
            (8, "AB-"),
        ]
        for code, label in bloodgroup_data:
            BloodGroupChoice.objects.get_or_create(
                code=code,
                defaults={"label": label, "is_active": True}
            )
            self.stdout.write(self.style.SUCCESS(f"✓ Blood Group: {label}"))

        # Marital Status Choices
        maritalstatus_data = [
            (1, "Single"),
            (2, "Married"),
            (3, "Divorced"),
            (4, "Widowed"),
            (5, "Separated"),
        ]
        for code, label in maritalstatus_data:
            MaritalStatusChoice.objects.get_or_create(
                code=code,
                defaults={"label": label, "is_active": True}
            )
            self.stdout.write(self.style.SUCCESS(f"✓ Marital Status: {label}"))

        # Education Choices
        education_data = [
            (1, "Below 10th"),
            (2, "10th Pass"),
            (3, "12th Pass"),
            (4, "Diploma"),
            (5, "Bachelor"),
            (6, "Master"),
            (7, "PhD"),
            (8, "Other"),
        ]
        for code, label in education_data:
            EducationChoice.objects.get_or_create(
                code=code,
                defaults={"label": label, "is_active": True}
            )
            self.stdout.write(self.style.SUCCESS(f"✓ Education: {label}"))

        # Skill Choices
        skill_data = [
            (1, "First Aid"),
            (2, "Disaster Management"),
            (3, "Rescue Operations"),
            (4, "Community Care"),
            (5, "Training"),
            (6, "Other"),
        ]
        for code, label in skill_data:
            SkillChoice.objects.get_or_create(
                code=code,
                defaults={"label": label, "is_active": True}
            )
            self.stdout.write(self.style.SUCCESS(f"✓ Skill: {label}"))

        # Area Type Choices
        areatype_data = [
            (1, "Urban"),
            (2, "Rural"),
            (3, "Semi-Urban"),
        ]
        for code, label in areatype_data:
            AreaTypeChoice.objects.get_or_create(
                code=code,
                defaults={"label": label, "is_active": True}
            )
            self.stdout.write(self.style.SUCCESS(f"✓ Area Type: {label}"))

        self.stdout.write(self.style.SUCCESS("\n✅ All volunteer choices seeded successfully!"))
