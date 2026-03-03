# Generated migration for OrganizationType model with proper data handling
from django.db import migrations, models
import django.db.models.deletion


def create_default_org_types(apps, schema_editor):
    """Create default organization types"""
    OrganizationType = apps.get_model('models', 'OrganizationType')
    
    org_types_data = [
        ('NCC', 'National Cadet Corps', 'Military youth organization'),
        ('NSS', 'National Service Scheme', 'Social service organization'),
        ('BSG', 'Bharat Scouts & Guides', 'Youth development organization'),
        ('NYKS', 'National Youth Korps Society', 'Youth welfare organization'),
    ]
    
    for code, name, desc in org_types_data:
        OrganizationType.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'description': desc,
                'is_active': True
            }
        )


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0004_remove_user_block_code_remove_user_district_code_and_more'),
    ]

    operations = [
        # Step 1: Create OrganizationType table
        migrations.CreateModel(
            name='OrganizationType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(db_index=True, max_length=50, unique=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Organization Type',
                'verbose_name_plural': 'Organization Types',
                'db_table': 'organization_types',
                'ordering': ['code'],
            },
        ),
        
        # Step 2: Insert default organization types
        migrations.RunPython(create_default_org_types, migrations.RunPython.noop),
        
        # Step 3: Make org_type nullable temporarily to allow migration
        migrations.AlterField(
            model_name='organization',
            name='org_type',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        
        # Step 4: Remove the CharField org_type
        migrations.RemoveField(
            model_name='organization',
            name='org_type',
        ),
        
        # Step 5: Add new ForeignKey org_type field (nullable initially)
        migrations.AddField(
            model_name='organization',
            name='org_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='organizations', to='models.organizationtype'),
        ),
    ]


