from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('code', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('module', models.CharField(max_length=100)),
                ('action', models.CharField(max_length=100)),
            ],
            options={'db_table': 'permissions', 'ordering': ['module', 'action']},
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(choices=[('SUPER_ADMIN', 'Super Admin'), ('TECHNICAL_ADMIN', 'Technical Admin'), ('NDMA_ADMIN', 'NDMA Admin'), ('SDMA_ADMIN', 'SDMA Admin'), ('DDMA_NODAL_OFFICER', 'DDMA Nodal Officer'), ('TRAINING_INSTITUTE', 'Training Institute'), ('YOUTH_ORG_ADMIN', 'Youth Organisation Admin'), ('VOLUNTEER', 'Volunteer'), ('PUBLIC_USER', 'Public User')], max_length=100, unique=True)),
                ('description', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('hierarchy_level', models.IntegerField(default=0)),
                ('permissions', models.ManyToManyField(blank=True, related_name='roles', to='models.permission')),
            ],
            options={'db_table': 'roles', 'ordering': ['hierarchy_level']},
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('state', models.CharField(blank=True, max_length=100, null=True)),
                ('district', models.CharField(blank=True, max_length=100, null=True)),
                ('organization', models.CharField(blank=True, max_length=255, null=True)),
                ('designation', models.CharField(blank=True, max_length=255, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_mfa_enabled', models.BooleanField(default=False)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='users', to='models.role')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_role', to=settings.AUTH_USER_MODEL)),
            ],
            options={'db_table': 'user_roles'},
        ),
        migrations.CreateModel(
            name='RolePermissionAudit',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('action', models.CharField(max_length=50)),
                ('details', models.JSONField(default=dict)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('permission', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='models.permission')),
                ('role', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='models.role')),
                ('target_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='role_changes', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='permission_audits', to=settings.AUTH_USER_MODEL)),
            ],
            options={'db_table': 'role_permission_audits', 'ordering': ['-created_at']},
        ),
    ]