from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orgs", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="organization",
            name="billing_status",
            field=models.CharField(
                choices=[("trial_locked", "Trial locked"), ("paid", "Paid")],
                default="trial_locked",
                max_length=32,
            ),
        ),
        migrations.AddField(
            model_name="organization",
            name="stripe_customer_id",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="organization",
            name="stripe_checkout_session_id",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="organization",
            name="paid_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

