# Generated migration for BulkUploadSession model and Volunteer.bulk_upload_session field

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('models', '0009_alter_volunteer_mis_id'),
    ]

    operations = [
        # Create BulkUploadSession model
        migrations.CreateModel(
            name='BulkUploadSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('volunteers_created', models.IntegerField(default=0)),
                ('total_rows_in_file', models.IntegerField(default=0)),
                ('error_count', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('success', 'All rows processed successfully'), ('partial', 'Some rows had errors'), ('failed', 'Upload failed')], default='success', max_length=20)),
                ('file_name', models.CharField(blank=True, max_length=255, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('district', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='models.district')),
                ('organization', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='models.organization')),
                ('state', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='models.state')),
                ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bulk_upload_sessions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-uploaded_at'],
            },
        ),
        
        # Add bulk_upload_session field to Volunteer
        migrations.AddField(
            model_name='volunteer',
            name='bulk_upload_session',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_volunteers', to='models.bulkuploadsession'),
        ),
        
        # Add indexes for BulkUploadSession
        migrations.AddIndex(
            model_name='bulkuploadsession',
            index=models.Index(fields=['state', 'district', 'uploaded_at'], name='models_bulk_state_d_idx'),
        ),
        migrations.AddIndex(
            model_name='bulkuploadsession',
            index=models.Index(fields=['organization', 'uploaded_at'], name='models_bulk_org_idx'),
        ),
        migrations.AddIndex(
            model_name='bulkuploadsession',
            index=models.Index(fields=['uploaded_by', 'uploaded_at'], name='models_bulk_user_idx'),
        ),
    ]
