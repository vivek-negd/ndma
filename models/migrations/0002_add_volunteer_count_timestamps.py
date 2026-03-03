# Generated manually - Add volunteer_count and timestamps to State and District

from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='state',
            name='volunteer_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='state',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='state',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='state',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='district',
            name='volunteer_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='district',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='district',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='district',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
