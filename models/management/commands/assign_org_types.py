from django.core.management.base import BaseCommand
from models.organization import Organization
from models.organization_type import OrganizationType


class Command(BaseCommand):
    help = 'Assign organization types to organizations'

    def handle(self, *args, **options):
        # Use EXISTING organization types from the table
        # 1 = NCC, 2 = NSS, 3 = BSG, 4 = NYKS
        
        ncc = OrganizationType.objects.get(id=1)      # NCC
        nss = OrganizationType.objects.get(id=2)      # NSS - Social Service
        bsg = OrganizationType.objects.get(id=3)      # BSG - Scouts & Guides
        nyks = OrganizationType.objects.get(id=4)     # NYKS
        
        # Assign organization types to organizations by ID
        assignments = [
            (2, nss),           # Red Cross - Maharashtra → NSS (Social Service)
            (3, ncc),           # NCC Unit Puducherry → NCC
            (4, ncc),           # Test Organization → NCC
        ]
        
        for org_id, org_type in assignments:
            try:
                org = Organization.objects.get(id=org_id)
                org.org_type = org_type
                org.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'[OK] Updated ID {org_id}: {org.name} -> {org.org_type.code} ({org.org_type.name})'
                    )
                )
            except Organization.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f'[SKIP] ID {org_id} not found'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'[ERROR] Error updating ID {org_id}: {str(e)}'
                    )
                )
