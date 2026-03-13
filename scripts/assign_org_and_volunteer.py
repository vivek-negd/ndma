import os
import django
import sys
from pathlib import Path

# Ensure project root is on sys.path so Django settings can be imported
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from django.contrib.auth import get_user_model
from models.state import State
from models.district import District
from models.organization_type import OrganizationType
from models.organization import Organization
from models.volunteer import Volunteer
from models.role import UserRole

User = get_user_model()

TARGET_USER_ID = 44
STATE_ID = 4
DISTRICT_ID = 47
ORG_NAME = 'Youth Org Katihar (auto)'
ORG_TYPE_CODE = 'YOUTH_ORG'

try:
    user = User.objects.get(id=TARGET_USER_ID)
except Exception as e:
    print('User not found:', e)
    sys.exit(1)

try:
    state = State.objects.get(id=STATE_ID)
    district = District.objects.get(id=DISTRICT_ID)
except Exception as e:
    print('State/District lookup failed:', e)
    sys.exit(1)

org_type, _ = OrganizationType.objects.get_or_create(code=ORG_TYPE_CODE, defaults={'name': 'Youth Organisation'})

org, created = Organization.objects.get_or_create(
    name=ORG_NAME,
    state=state,
    district=district,
    defaults={'org_type': org_type, 'contact_person': user.name or '', 'contact_email': user.email_address or ''}
)

print('Organization:', org.id, org.name, 'created=' + str(created))

# Assign UserRole.organization to this org
user_role = UserRole.objects.filter(user=user).first()
if not user_role:
    print('UserRole for user not found; creating one with role YOUTH_ORG_ADMIN')
    from models.role import Role
    role = Role.objects.filter(name='YOUTH_ORG_ADMIN').first()
    if not role:
        print('Role YOUTH_ORG_ADMIN not found; aborting')
        sys.exit(1)
    user_role = UserRole.objects.create(user=user, role=role, organization=str(org.id), state=str(state.id), district=str(district.id), is_active=True)
    print('Created UserRole', user_role.id)
else:
    user_role.organization = str(org.id)
    user_role.state = str(state.id)
    user_role.district = str(district.id)
    user_role.save()
    print('Updated UserRole', user_role.id, 'organization ->', user_role.organization)

# Create a sample volunteer in this organization if none exists
sample_mis_id = 999999
if not Volunteer.objects.filter(mis_id=sample_mis_id).exists():
    v = Volunteer.objects.create(mis_id=sample_mis_id, name='Auto Volunteer', organization=org, state=state, district=district, email='auto.vol@example.com')
    print('Created volunteer', v.id)
else:
    print('Sample volunteer already exists')

print('Done')
