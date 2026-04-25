import uuid

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("orgs", "0002_org_billing_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="PilotIntake",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("contact_name", models.CharField(max_length=255)),
                ("contact_email", models.EmailField(max_length=254)),
                ("use_case", models.TextField()),
                ("doc_types", models.TextField(blank=True, default="")),
                ("success_criteria", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "organization",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="pilot_intakes", to="orgs.organization"),
                ),
            ],
        ),
    ]

