"""Add missing volunteer *_id fields that are absent in DB.

This migration adds integer columns and mybharat_id char field to
`models_volunteer` to match the current model definition where these
columns are expected but were not present in the database.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0009_alter_volunteer_mis_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="volunteer",
            name="gender_id",
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="volunteer",
            name="bloodgroup_id",
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="volunteer",
            name="salutation_id",
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="volunteer",
            name="maritalstatus_id",
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="volunteer",
            name="education_id",
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="volunteer",
            name="skill_id",
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="volunteer",
            name="area_type_id",
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="volunteer",
            name="mybharat_id",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
