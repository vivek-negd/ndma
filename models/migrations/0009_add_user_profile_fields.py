from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0008_merge_20260301_2100"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="name",
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="user",
            name="mobile",
            field=models.CharField(max_length=15, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="user",
            name="designation",
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="user",
            name="aadhar",
            field=models.CharField(max_length=12, null=True, blank=True),
        ),
    ]
