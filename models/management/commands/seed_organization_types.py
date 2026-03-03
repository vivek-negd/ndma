from django.core.management.base import BaseCommand
from models.organization_type import OrganizationType


class Command(BaseCommand):
    help = 'Seed organization types (NCC, NSS, BSG, NYKS)'

    def handle(self, *args, **options):
        org_types = [
            {
                'code': 'NCC',
                'name': 'National Cadet Corps',
                'description': 'Military youth organization for school and college students'
            },
            {
                'code': 'NSS',
                'name': 'National Service Scheme',
                'description': 'Social service organization for youth development'
            },
            {
                'code': 'BSG',
                'name': 'Bharat Scouts & Guides',
                'description': 'Youth development organization providing outdoor education'
            },
            {
                'code': 'NYKS',
                'name': 'National Youth Korps Society',
                'description': 'Youth organization promoting national interest and social welfare'
            },
        ]

        for org_type_data in org_types:
            org_type, created = OrganizationType.objects.get_or_create(
                code=org_type_data['code'],
                defaults={
                    'name': org_type_data['name'],
                    'description': org_type_data['description'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Created: {org_type.code} - {org_type.name}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'⊘ Already exists: {org_type.code} - {org_type.name}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS('\n✓ All organization types seeded successfully!')
        )
