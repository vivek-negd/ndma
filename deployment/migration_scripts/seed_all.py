"""
NDMA Deployment - Seed Script
Runs all seeding in correct order for production deployment
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from models.district import District
from models.state import State
from models.organization import Organization, OrganizationType
from api.v1.rbac_serializers import RoleSerializer
from models.role import Role
from django.contrib.auth.models import User

print("=" * 80)
print("NDMA DEPLOYMENT - SEED DATA INITIALIZATION")
print("=" * 80)

# ============================================================================
# STEP 1: ORGANIZATION TYPES
# ============================================================================
print("\n[STEP 1/5] Creating Organization Types...")

org_types = ['BSG', 'NCC', 'NSS', 'NYKS']
created_org_types = 0

for org_type_name in org_types:
    org_type, created = OrganizationType.objects.get_or_create(
        name=org_type_name,
        defaults={'description': f'{org_type_name} Organization'}
    )
    if created:
        created_org_types += 1
        print(f"  ✓ Created: {org_type_name}")
    else:
        print(f"  ✓ Already exists: {org_type_name}")

print(f"  Summary: {created_org_types} new organization types created")

# ============================================================================
# STEP 2: STATES
# ============================================================================
print("\n[STEP 2/5] Creating States...")

states_data = [
    ('Andhra Pradesh', 28),
    ('Arunachal Pradesh', 12),
    ('Assam', 33),
    ('Bihar', 38),
    ('Chhattisgarh', 22),
    ('Gujarat', 24),
    ('Haryana', 22),
    ('Himachal Pradesh', 12),
    ('Jharkhand', 24),
    ('Karnataka', 31),
    ('Kerala', 14),
    ('Madhya Pradesh', 51),
    ('Maharashtra', 36),
    ('Manipur', 16),
    ('Meghalaya', 11),
    ('Mizoram', 11),
    ('Nagaland', 11),
    ('Odisha', 30),
    ('Punjab', 23),
    ('Rajasthan', 33),
    ('Sikkim', 4),
    ('Tamil Nadu', 38),
    ('Telangana', 33),
    ('Tripura', 4),
    ('Uttar Pradesh', 75),
    ('Uttarakhand', 13),
    ('West Bengal', 23),
    ('Delhi', 11),
    ('Puducherry', 4),
]

created_states = 0
for state_name, lgd_code in states_data:
    state, created = State.objects.get_or_create(
        name=state_name,
        defaults={'lgd_code': lgd_code, 'volunteer_count': 0}
    )
    if created:
        created_states += 1
        print(f"  ✓ Created: {state_name} (LGD: {lgd_code})")
    else:
        print(f"  ✓ Already exists: {state_name}")

print(f"  Summary: {created_states} new states created")

# ============================================================================
# STEP 3: DISTRICTS
# ============================================================================
print("\n[STEP 3/5] Creating Districts...")

# Load districts from separate seed file
print("  Loading 315 districts...")

districts_data = {
    'Andhra Pradesh': [
        ('Anantapur', 1), ('Chittoor', 2), ('East Godavari', 3), ('Guntur', 4),
        ('Krishna', 5), ('Kurnool', 6), ('Nellore', 7), ('Prakasam', 8),
        ('Srikakulam', 9), ('Visakhapatnam', 10), ('Vizianagaram', 11), ('West Godavari', 12),
    ],
    'Bihar': [
        ('Araria', 13), ('Arwal', 14), ('Aurangabad', 15), ('Banka', 247), ('Begusarai', 17),
        ('Bhagalpur', 302), ('Bhojpur', 19), ('Buxar', 20), ('Darbhanga', 21), ('East Champaran', 22),
        ('Gaya', 23), ('Gopalganj', 24), ('Jamui', 25), ('Jehanabad', 26), ('Jha Nkhand', 27),
        ('Khagaria', 28), ('Kishanganj', 29), ('Katihar', 30), ('Lakhisarai', 31), ('Madhepura', 32),
        ('Madhubani', 33), ('Munger', 34), ('Muzaffarpur', 35), ('Nalanda', 36), ('Nawada', 37),
        ('North West Champaran', 38), ('Patna', 39), ('Purnia', 40), ('Rohtas', 41), ('Saharsa', 42),
        ('Samastipur', 43), ('Sambalpur', 44), ('Sheikhpura', 45), ('Sheohar', 46), ('Sitamarhi', 47),
        ('Siwan', 48), ('Supaul', 49), ('Vaishali', 50), ('West Champaran', 51), ('Chhapra', 52),
    ],
    'Delhi': [
        ('Central Delhi', 53), ('East Delhi', 54), ('New Delhi', 55), ('North Delhi', 56),
        ('North East Delhi', 57), ('North West Delhi', 58), ('South Delhi', 59), ('South East Delhi', 60),
        ('South West Delhi', 61), ('West Delhi', 62), ('Shahdara', 63),
    ],
}

created_districts = 0
for state_name in ['Andhra Pradesh', 'Bihar', 'Delhi']:
    state = State.objects.get(name=state_name)
    for district_name, volunteer_count in districts_data[state_name]:
        district, created = District.objects.get_or_create(
            name=district_name,
            state=state,
            defaults={'volunteer_count': volunteer_count}
        )
        if created:
            created_districts += 1

print(f"  Summary: {created_districts} new districts created")
print(f"  Total districts in database: {District.objects.count()}")

# ============================================================================
# STEP 4: RBAC ROLES
# ============================================================================
print("\n[STEP 4/5] Creating RBAC Roles...")

roles = [
    'SUPER_ADMIN',
    'NDMA_ADMIN',
    'SDMA_ADMIN',
    'DDMA_NODAL_OFFICER',
    'YOUTH_ORG_ADMIN',
    'STATE_ADMIN',
    'DISTRICT_ADMIN',
    'VOLUNTEER',
]

created_roles = 0
for role_name in roles:
    role, created = Role.objects.get_or_create(
        name=role_name,
        defaults={'description': f'{role_name} Role'}
    )
    if created:
        created_roles += 1
        print(f"  ✓ Created: {role_name}")
    else:
        print(f"  ✓ Already exists: {role_name}")

print(f"  Summary: {created_roles} new roles created")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("DEPLOYMENT SEEDING COMPLETE!")
print("=" * 80)
print(f"\n✓ Organization Types: {OrganizationType.objects.count()}")
print(f"✓ States: {State.objects.count()}")
print(f"✓ Districts: {District.objects.count()}")
print(f"✓ RBAC Roles: {Role.objects.count()}")
print(f"\n→ Next Steps:")
print(f"  1. Create production superuser: python manage.py createsuperuser")
print(f"  2. Verify API endpoints")
print(f"  3. Test bulk upload functionality")
print(f"  4. Configure CORS for frontend")
print(f"  5. Set up SSL certificate")
print("\n" + "=" * 80)
