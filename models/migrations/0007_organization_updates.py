# Generated migration
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0005_district_lgd_code_state_lgd_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AddField(
            model_name='organization',
            name='org_type',
            field=models.CharField(
                choices=[
                    ('NCC', 'National Cadet Corps'),
                    ('NSS', 'National Service Scheme'),
                    ('BSG', 'Bharat Scouts & Guides'),
                    ('NYKS', 'National Youth Korps Society'),
                ],
                default='OTHER',
                max_length=50,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='organization',
            name='state',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='organizations',
                to='models.state',
            ),
        ),
        migrations.AddField(
            model_name='organization',
            name='district',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='organizations',
                to='models.district',
            ),
        ),
        migrations.AddField(
            model_name='organization',
            name='contact_person',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='organization',
            name='contact_email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='organization',
            name='contact_phone',
            field=models.CharField(blank=True, max_length=15),
        ),
        migrations.AddField(
            model_name='organization',
            name='address',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='website',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterUniqueTogether(
            name='organization',
            unique_together={('name', 'state', 'district')},
        ),
        migrations.AlterModelOptions(
            name='organization',
            options={'ordering': ['org_type', 'name']},
        ),
    ]
