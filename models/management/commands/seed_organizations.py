from django.core.management.base import BaseCommand
from models.organization import Organization


ORGS = [
    "National Cadet Corps (NCC)",
    "Nehru Yuva Kendra Sangathan (NYKS)",
    "National Service Scheme (NSS)",
    "Bharat Scouts & Guides (BS&G)",
]


class Command(BaseCommand):
    help = "Seed fixed youth organizations"

    def handle(self, *args, **options):
        created = 0
        for name in ORGS:
            obj, was_created = Organization.objects.get_or_create(name=name)
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded organizations. Created: {created}, total: {Organization.objects.count()}"))
