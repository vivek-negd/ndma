from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0009_add_user_profile_fields"),
    ]

    operations = [
        # Alter name field to be NOT NULL with default for existing rows
        migrations.AlterField(
            model_name="user",
            name="name",
            field=models.CharField(max_length=255, default=""),
            preserve_default=False,
        ),
        # Alter mobile field to be NOT NULL with default for existing rows
        migrations.AlterField(
            model_name="user",
            name="mobile",
            field=models.CharField(
                max_length=15,
                validators=[
                    django.core.validators.RegexValidator(
                        r"^\d{10}$", "Enter a 10 digit mobile number"
                    )
                ],
                default="0000000000",
            ),
            preserve_default=False,
        ),
        # Alter designation field to be NOT NULL with default for existing rows
        migrations.AlterField(
            model_name="user",
            name="designation",
            field=models.CharField(max_length=255, default=""),
            preserve_default=False,
        ),
        # Alter aadhar field to be NOT NULL with default for existing rows
        migrations.AlterField(
            model_name="user",
            name="aadhar",
            field=models.CharField(
                max_length=12,
                validators=[
                    django.core.validators.RegexValidator(
                        r"^\d{12}$", "Enter a 12 digit Aadhar number"
                    )
                ],
                default="000000000000",
            ),
            preserve_default=False,
        ),
        # Alter state_code field to be NOT NULL with default for existing rows
        migrations.AlterField(
            model_name="user",
            name="state_code",
            field=models.CharField(max_length=10, default=""),
            preserve_default=False,
        ),
    ]
