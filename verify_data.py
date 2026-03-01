"""
Display all users in table format to verify data is correct.
Run: python verify_data.py
"""
import os
import django
from tabulate import tabulate

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()


def display_users_table():
    """Display all users in a formatted table"""
    users = User.objects.all().values(
        'id', 'email_address', 'name', 'mobile', 'designation', 'aadhar',
        'user_role', 'state_code', 'district_code', 'block_code', 'is_active', 'created_at'
    )
    
    if not users:
        print("No users found in database.")
        return
    
    # Convert to list of dicts for tabulate
    data = []
    for user in users:
        data.append([
            user['id'],
            user['email_address'],
            user['name'],
            user['mobile'],
            user['designation'],
            user['aadhar'],
            user['user_role'],
            user['state_code'],
            user['district_code'],
            user['block_code'],
            'Yes' if user['is_active'] else 'No',
            user['created_at'].strftime('%Y-%m-%d %H:%M:%S') if user['created_at'] else ''
        ])
    
    headers = [
        'ID', 'Email', 'Name', 'Mobile', 'Designation', 'Aadhar',
        'Role', 'State', 'District', 'Block', 'Active', 'Created At'
    ]
    
    print("\n" + "=" * 200)
    print("ALL USERS IN DATABASE")
    print("=" * 200)
    print(tabulate(data, headers=headers, tablefmt='grid'))
    print("=" * 200)
    print(f"Total Users: {len(data)}\n")


def display_user_detail(user_id=None, email=None):
    """Display detailed info for a specific user"""
    if user_id:
        user = User.objects.filter(id=user_id).first()
    elif email:
        user = User.objects.filter(email_address=email).first()
    else:
        return
    
    if not user:
        print(f"User not found")
        return
    
    print("\n" + "=" * 80)
    print(f"USER DETAIL: {user.email_address}")
    print("=" * 80)
    detail = [
        ['ID', user.id],
        ['Email', user.email_address],
        ['Name', user.name],
        ['Mobile', user.mobile],
        ['Designation', user.designation],
        ['Aadhar', user.aadhar],
        ['User Role', user.user_role],
        ['State Code', user.state_code],
        ['District Code', user.district_code],
        ['Block Code', user.block_code],
        ['Is Active', 'Yes' if user.is_active else 'No'],
        ['Is Staff', 'Yes' if user.is_staff else 'No'],
        ['Is Superuser', 'Yes' if user.is_superuser else 'No'],
        ['Created At', user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else 'N/A'],
        ['Permissions', ', '.join(user.get_effective_permissions())],
    ]
    print(tabulate(detail, tablefmt='grid'))
    print("=" * 80 + "\n")


def verify_required_fields():
    """Check if all users have required fields filled"""
    print("\n" + "=" * 80)
    print("VERIFICATION: Required Fields")
    print("=" * 80)
    
    users = User.objects.all()
    errors = []
    
    for user in users:
        issues = []
        if not user.name:
            issues.append("name is empty")
        if not user.mobile:
            issues.append("mobile is empty")
        if not user.designation:
            issues.append("designation is empty")
        if not user.aadhar:
            issues.append("aadhar is empty")
        if not user.state_code:
            issues.append("state_code is empty")
        
        if issues:
            errors.append([user.email_address, ', '.join(issues)])
    
    if errors:
        print("⚠️  WARNINGS - Missing required fields:")
        print(tabulate(errors, headers=['Email', 'Issues'], tablefmt='grid'))
    else:
        print("✅ ALL USERS have all required fields filled!")
    print("=" * 80 + "\n")


def main():
    print("\n🔍 DATA VERIFICATION TOOL\n")
    
    while True:
        print("Options:")
        print("1. Show all users (table)")
        print("2. Show user detail by ID")
        print("3. Show user detail by email")
        print("4. Verify all required fields")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            display_users_table()
        elif choice == '2':
            user_id = input("Enter user ID: ").strip()
            if user_id.isdigit():
                display_user_detail(user_id=int(user_id))
            else:
                print("Invalid ID")
        elif choice == '3':
            email = input("Enter email: ").strip()
            display_user_detail(email=email)
        elif choice == '4':
            verify_required_fields()
        elif choice == '5':
            print("Goodbye!")
            break
        else:
            print("Invalid option")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
