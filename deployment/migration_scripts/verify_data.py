"""
NDMA Deployment - Data Verification Script
Verify all seeded data is correct
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from models.district import District
from models.state import State
from models.organization import OrganizationType
from models.role import Role
from models.volunteer import Volunteer

print("=" * 80)
print("NDMA DEPLOYMENT - DATA VERIFICATION")
print("=" * 80)

# Check organization types
print("\n[CHECK 1] Organization Types")
org_types_count = OrganizationType.objects.count()
org_types = list(OrganizationType.objects.values_list('name', flat=True))
print(f"  Count: {org_types_count}")
if org_types_count == 4:
    print(f"  ✓ PASSED - Found 4 organization types")
    print(f"    Types: {', '.join(org_types)}")
else:
    print(f"  ✗ FAILED - Expected 4, found {org_types_count}")

# Check states
print("\n[CHECK 2] States")
states_count = State.objects.count()
print(f"  Count: {states_count}")
if states_count == 29:
    print(f"  ✓ PASSED - Found 29 states")
else:
    print(f"  ✗ FAILED - Expected 29, found {states_count}")

# Sample states
sample_states = State.objects.values('id', 'name')[:3]
for state in sample_states:
    print(f"    ID {state['id']}: {state['name']}")

# Check districts
print("\n[CHECK 3] Districts")
districts_count = District.objects.count()
print(f"  Count: {districts_count}")
if districts_count >= 300:
    print(f"  ✓ PASSED - Found {districts_count} districts")
else:
    print(f"  ✗ FAILED - Expected ~315, found {districts_count}")

# Check districts by state
print("\n[CHECK 4] District-State Mapping")
state_district_mapping = {}
for state in State.objects.all():
    count = District.objects.filter(state=state).count()
    if count > 0:
        state_district_mapping[state.name] = count

print(f"  States with districts: {len(state_district_mapping)}")
for state_name, district_count in list(state_district_mapping.items())[:5]:
    print(f"    {state_name}: {district_count} districts")

# Check volunteer counts
print("\n[CHECK 5] Volunteer Counts")
total_volunteers = 0
for district in District.objects.all():
    total_volunteers += district.volunteer_count

print(f"  Total volunteer count across districts: {total_volunteers}")
if total_volunteers > 4000:
    print(f"  ✓ PASSED - Found {total_volunteers} volunteers (expected ~4112)")
else:
    print(f"  ⚠ WARNING - Low volunteer count: {total_volunteers}")

# Top districts by volunteers
print("\n[CHECK 6] Top Districts by Volunteer Count")
top_districts = District.objects.order_by('-volunteer_count')[:5]
for idx, district in enumerate(top_districts, 1):
    print(f"  {idx}. {district.name} ({district.state.name}): {district.volunteer_count} volunteers")

# Check RBAC roles
print("\n[CHECK 7] RBAC Roles")
roles_count = Role.objects.count()
roles = list(Role.objects.values_list('name', flat=True))
print(f"  Count: {roles_count}")
if roles_count == 8:
    print(f"  ✓ PASSED - Found 8 roles")
    for role in sorted(roles):
        print(f"    • {role}")
else:
    print(f"  ⚠ WARNING - Expected 8 roles, found {roles_count}")

# Database connectivity check
print("\n[CHECK 8] Database Connectivity")
try:
    # Try a simple query
    test_count = State.objects.count()
    print(f"  ✓ PASSED - Database connected (can access {test_count} states)")
except Exception as e:
    print(f"  ✗ FAILED - Database connection error: {str(e)}")

# Final summary
print("\n" + "=" * 80)
print("VERIFICATION SUMMARY")
print("=" * 80)

all_checks = {
    'Organization Types': org_types_count == 4,
    'States': states_count == 29,
    'Districts': districts_count >= 300,
    'District-State Mapping': len(state_district_mapping) > 20,
    'Volunteer Counts': total_volunteers > 4000,
    'RBAC Roles': roles_count == 8,
}

passed_checks = sum(1 for v in all_checks.values() if v)
total_checks = len(all_checks)

print(f"\n✓ Passed: {passed_checks}/{total_checks}")
for check_name, passed in all_checks.items():
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"  {status}: {check_name}")

if passed_checks == total_checks:
    print("\n" + "🎉 " * 20)
    print("ALL CHECKS PASSED - READY FOR DEPLOYMENT!")
    print("🎉 " * 20)
else:
    print(f"\n⚠ {total_checks - passed_checks} check(s) failed - review above")

print("\n" + "=" * 80)
print("Next steps:")
print("  1. Create superuser: python manage.py createsuperuser")
print("  2. Test API endpoints")
print("  3. Configure frontend CORS")
print("  4. Deploy to production")
print("=" * 80)
