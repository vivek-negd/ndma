from django.core.management.base import BaseCommand
from models.role import Permission, Role


class Command(BaseCommand):
    help = 'Seed initial RBAC permissions and roles'

    def handle(self, *args, **options):
        permissions_data = [
            {'name': 'View Volunteers', 'code': 'view_volunteer', 'module': 'volunteer', 'action': 'view'},
            {'name': 'Create Volunteer', 'code': 'create_volunteer', 'module': 'volunteer', 'action': 'create'},
            {'name': 'Edit Volunteer', 'code': 'edit_volunteer', 'module': 'volunteer', 'action': 'edit'},
            {'name': 'Delete Volunteer', 'code': 'delete_volunteer', 'module': 'volunteer', 'action': 'delete'},
            {'name': 'View Training', 'code': 'view_training', 'module': 'training', 'action': 'view'},
            {'name': 'Create Training', 'code': 'create_training', 'module': 'training', 'action': 'create'},
            {'name': 'Edit Training', 'code': 'edit_training', 'module': 'training', 'action': 'edit'},
            {'name': 'Delete Training', 'code': 'delete_training', 'module': 'training', 'action': 'delete'},
            {'name': 'Approve Training', 'code': 'approve_training', 'module': 'training', 'action': 'approve'},
            {'name': 'View Deployment', 'code': 'view_deployment', 'module': 'deployment', 'action': 'view'},
            {'name': 'Create Deployment', 'code': 'create_deployment', 'module': 'deployment', 'action': 'create'},
            {'name': 'Edit Deployment', 'code': 'edit_deployment', 'module': 'deployment', 'action': 'edit'},
            {'name': 'Delete Deployment', 'code': 'delete_deployment', 'module': 'deployment', 'action': 'delete'},
            {'name': 'Approve Deployment', 'code': 'approve_deployment', 'module': 'deployment', 'action': 'approve'},
            {'name': 'View Roles', 'code': 'view_role', 'module': 'rbac', 'action': 'view'},
            {'name': 'Manage Roles', 'code': 'manage_role', 'module': 'rbac', 'action': 'manage'},
            {'name': 'Assign Roles', 'code': 'assign_role', 'module': 'rbac', 'action': 'assign'},
            {'name': 'View Reports', 'code': 'view_reports', 'module': 'reports', 'action': 'view'},
            {'name': 'Export Reports', 'code': 'export_reports', 'module': 'reports', 'action': 'export'},
            {'name': 'View Audit Logs', 'code': 'view_audit_logs', 'module': 'system', 'action': 'view'},
            {'name': 'Manage Users', 'code': 'manage_users', 'module': 'system', 'action': 'manage'},
        ]
        
        for perm_data in permissions_data:
            Permission.objects.get_or_create(
                code=perm_data['code'],
                defaults={
                    'name': perm_data['name'],
                    'description': f"{perm_data['name']} - {perm_data['module']}",
                    'module': perm_data['module'],
                    'action': perm_data['action']
                }
            )
        
        self.stdout.write(self.style.SUCCESS('Permissions created successfully'))
        
        roles_data = [
            {
                'name': 'SUPER_ADMIN',
                'description': 'Super Administrator with full system access',
                'hierarchy_level': 0,
                'permissions': [p['code'] for p in permissions_data]
            },
            {
                'name': 'TECHNICAL_ADMIN',
                'description': 'Technical Administrator',
                'hierarchy_level': 1,
                'permissions': ['view_audit_logs', 'manage_users', 'view_role', 'view_reports']
            },
            {
                'name': 'NDMA_ADMIN',
                'description': 'NDMA Administrator',
                'hierarchy_level': 2,
                'permissions': ['view_volunteer', 'create_volunteer', 'edit_volunteer', 'view_training', 
                               'create_training', 'approve_training', 'view_deployment', 'approve_deployment', 'view_reports']
            },
            {
                'name': 'SDMA_ADMIN',
                'description': 'SDMA Administrator',
                'hierarchy_level': 3,
                'permissions': ['view_volunteer', 'create_volunteer', 'edit_volunteer', 'view_training', 
                               'create_training', 'view_deployment', 'view_reports']
            },
            {
                'name': 'DDMA_NODAL_OFFICER',
                'description': 'DDMA Nodal Officer',
                'hierarchy_level': 4,
                'permissions': ['view_volunteer', 'edit_volunteer', 'view_training', 'view_deployment', 'view_reports']
            },
            {
                'name': 'TRAINING_INSTITUTE',
                'description': 'Training Institute',
                'hierarchy_level': 5,
                'permissions': ['view_volunteer', 'create_training', 'edit_training', 'view_training']
            },
            {
                'name': 'YOUTH_ORG_ADMIN',
                'description': 'Youth Organisation Administrator',
                'hierarchy_level': 6,
                'permissions': ['view_volunteer', 'create_volunteer', 'view_training', 'view_deployment']
            },
            {
                'name': 'VOLUNTEER',
                'description': 'Volunteer User',
                'hierarchy_level': 7,
                'permissions': ['view_training', 'view_deployment']
            },
            {
                'name': 'PUBLIC_USER',
                'description': 'Public User with minimal access',
                'hierarchy_level': 9,
                'permissions': []
            },
        ]
        
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={
                    'description': role_data['description'],
                    'hierarchy_level': role_data['hierarchy_level'],
                    'is_active': True
                }
            )
            
            permission_objs = Permission.objects.filter(code__in=role_data['permissions'])
            role.permissions.set(permission_objs)
            
            status = 'Created' if created else 'Updated'
            self.stdout.write(self.style.SUCCESS(f'{status} role: {role_data["name"]}'))
        
        self.stdout.write(self.style.SUCCESS('RBAC seeding completed successfully'))
        