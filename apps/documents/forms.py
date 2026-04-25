from django import forms

from .models import Document


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["file"]

    def clean_file(self):
        f = self.cleaned_data["file"]
        name = (getattr(f, "name", "") or "").lower()
        if not name.endswith(".pdf"):
            raise forms.ValidationError("Only PDF files are allowed.")
        if getattr(f, "size", 0) and f.size > 20 * 1024 * 1024:
            raise forms.ValidationError("Max file size is 20MB.")
        return f

