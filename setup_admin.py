"""
Comprehensive setup script for initial NDMA API setup.
This ensures SUPER_ADMIN exists with all required fields.
Only SUPER_ADMIN/NDMA_ADMIN can create other users/states/organizations.
NO SIGNUP - all creation is admin-only.
"""
import os
import sys
import django
from getpass import getpass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()


def setup_initial_superadmin():
    """Create or verify SUPER_ADMIN exists with all required fields."""
    print("\n" + "=" * 70)
    print("NDMA API - Initial Setup")
    print("=" * 70)
    
    email = input("Enter SUPER_ADMIN email (default: admin@ndma.gov.in): ").strip() or "admin@ndma.gov.in"
    
    # Check if admin exists
    user = User.objects.filter(email_address=email).first()
    if user and user.user_role == 'SUPER_ADMIN':
        print(f"\n✓ SUPER_ADMIN already exists: {user.email_address}")
        update = input("Update password? (y/n): ").strip().lower()
        if update == 'y':
            password = getpass("Enter new password: ")
            user.set_password(password)
            user.save()
            print(f"✓ Password updated for {email}")
        return user
    
    # Create new SUPER_ADMIN
    print("\nCreating new SUPER_ADMIN account...")
    print("Note: All fields are REQUIRED (government onboarding form)")
    
    name = input("Enter full name: ").strip()
    while not name:
        print("❌ Name is required")
        name = input("Enter full name: ").strip()
    
    mobile = input("Enter mobile (10 digits): ").strip()
    while not mobile or len(mobile) != 10 or not mobile.isdigit():
        print("❌ Mobile must be exactly 10 digits")
        mobile = input("Enter mobile (10 digits): ").strip()
    
    designation = input("Enter designation: ").strip()
    while not designation:
        print("❌ Designation is required")
        designation = input("Enter designation: ").strip()
    
    aadhar = input("Enter Aadhar (12 digits): ").strip()
    while not aadhar or len(aadhar) != 12 or not aadhar.isdigit():
        print("❌ Aadhar must be exactly 12 digits")
        aadhar = input("Enter Aadhar (12 digits): ").strip()
    
    state_code = input("Enter state code (e.g., PY for Puducherry): ").strip().upper()
    while not state_code or len(state_code) > 2:
        print("❌ State code is required (max 2 chars)")
        state_code = input("Enter state code: ").strip().upper()
    
    password = getpass("Enter password: ")
    while len(password) < 8:
        print("❌ Password must be at least 8 characters")
        password = getpass("Enter password: ")
    
    # Create user
    try:
        user = User.objects.create_superuser(
            email_address=email,
            password=password,
            name=name,
            mobile=mobile,
            designation=designation,
            aadhar=aadhar,
            user_role='SUPER_ADMIN',
            state_code=state_code,
            is_active=True
        )
        print(f"\n✓ SUPER_ADMIN created successfully!")
        print(f"  Email: {user.email_address}")
        print(f"  Name: {user.name}")
        print(f"  Mobile: {user.mobile}")
        print(f"  Designation: {user.designation}")
        print(f"  Aadhar: {user.aadhar}")
        print(f"  State: {user.state_code}")
        return user
    except Exception as e:
        print(f"\n❌ Error creating SUPER_ADMIN: {e}")
        sys.exit(1)


def show_next_steps():
    """Show how to use the API."""
    print("\n" + "=" * 70)
    print("Next Steps - Creating Users via API")
    print("=" * 70)
    print("""
1. LOGIN as SUPER_ADMIN:
   POST /api/v1/auth/login/
   {
     "email": "admin@ndma.gov.in",
     "password": "<your_password>"
   }
   Response: { "access": "<TOKEN>", "user": {...} }

2. CREATE NEW USER (SUPER_ADMIN Only):
   POST /api/v1/auth/create_user/
   Headers: Authorization: Bearer <TOKEN>
   
   Required fields:
   {
     "email": "user@example.com",
     "password": "SecurePass123!",
     "name": "Full Name",
     "mobile": "9999999999",
     "designation": "Title",
     "aadhar": "123456789012",
     "user_role": "SDMA_ADMIN",     // or DDMA_NODAL_OFFICER, YOUTH_ORG_ADMIN, etc.
     "state_code": "PY",            // REQUIRED
     "district_code": null,         // optional
     "block_code": null,            // optional
     "is_active": true
   }

3. CREATE ORGANIZATIONS:
   POST /api/v1/organizations/
   Headers: Authorization: Bearer <TOKEN_FROM_ADMIN>
   {
     "name": "NCC Unit Name",
     "org_type": "NCC",             // NCC, NSS, BSG, NYKS
     "state": <state_id>,           // FK to State
     "district": <district_id>,     // FK to District
     "contact_person": "Name",
     "contact_email": "contact@example.com",
     "contact_phone": "9999999999",
     "address": "Full address",
     "website": "https://example.com",
     "is_active": true
   }

4. ASSIGN ROLES TO USERS (Optional UserRole mapping):
   POST /api/v1/rbac/user-roles/
   Headers: Authorization: Bearer <TOKEN_FROM_ADMIN>
   {
     "user": <user_id>,
     "role": <role_id>,
     "state": "PY",
     "organization": null,
     "designation": "Officer",
     "is_active": true
   }

Important:
- NO SIGNUP ENDPOINT: Only SUPER_ADMIN/NDMA_ADMIN can create users
- ALL PROFILE FIELDS ARE REQUIRED: name, mobile, designation, aadhar, state_code
- NO HARDCODING: Provide actual values for each user/org
""")


if __name__ == '__main__':
    user = setup_initial_superadmin()
    show_next_steps()
    print("\n" + "=" * 70)
    print("Setup Complete!")
    print("=" * 70)
