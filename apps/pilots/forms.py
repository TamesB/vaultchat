from django import forms

from .models import PilotIntake


class PilotIntakeForm(forms.ModelForm):
    class Meta:
        model = PilotIntake
        fields = ["contact_name", "contact_email", "use_case", "doc_types", "success_criteria"]
        widgets = {
            "use_case": forms.Textarea(attrs={"rows": 4}),
            "doc_types": forms.Textarea(attrs={"rows": 3}),
            "success_criteria": forms.Textarea(attrs={"rows": 3}),
        }

