from django import forms
from django.core.exceptions import ValidationError
from .models import Offender, SEVERITY
import datetime

class OffenderForm(forms.ModelForm):
    # optional quick actions (handled by the view)
    warning_now = forms.BooleanField(required=False, label="Create a Warning now?")
    warning_severity = forms.ChoiceField(required=False, choices=SEVERITY, label="Warning Severity")
    ban_now = forms.BooleanField(required=False, label="Create a Ban now?")
    ban_duration = forms.ChoiceField(
        required=False,
        choices=[
            ("", "N/A"),
            ("1", "1 day"), ("3", "3 days"), ("7", "1 week"),
            ("14", "2 weeks"), ("30", "1 month"), ("90", "3 months"),
            ("365", "1 year"), ("permanent", "Permanent"),
        ],
        label="Ban Duration",
    )
    ban_reason = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}), label="Ban Reason")

    class Meta:
        model = Offender
        fields = [
            "name", "contact_info", "age", "date_of_birth", "sex",
            "height", "weight", "hair_color", "eye_color",
            "occupation", "address", "photo", "notes",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "bg-gray-50 border border-gray-300 text-sm rounded-lg w-full p-2.5", "placeholder": "Full name"}),
            "contact_info": forms.Textarea(attrs={"class": "bg-gray-50 border border-gray-300 text-sm rounded-lg w-full p-2.5", "rows": 3}),
            "age": forms.NumberInput(attrs={"class": "bg-gray-50 border border-gray-300 text-sm rounded-lg w-full p-2.5", "min": 1, "max": 150}),
            "date_of_birth": forms.DateInput(attrs={"class": "bg-gray-50 border border-gray-300 text-sm rounded-lg w-full p-2.5", "type": "date"}),
            "sex": forms.Select(attrs={"class": "bg-gray-50 border border-gray-300 text-sm rounded-lg w-full p-2.5"}),
            "height": forms.TextInput(attrs={"class": "bg-gray-50 border border-gray-300 text-sm rounded-lg w-full p-2.5"}),
            "weight": forms.TextInput(attrs={"class": "bg-gray-50 border border-gray-300 text-sm rounded-lg w-full p-2.5"}),
            "hair_color": forms.TextInput(attrs={"class": "bg-gray-50 border border-gray-300 text-sm rounded-lg w-full p-2.5"}),
            "eye_color": forms.TextInput(attrs={"class": "bg-gray-50 border border-gray-300 text-sm rounded-lg w-full p-2.5"}),
            "occupation": forms.TextInput(attrs={"class": "bg-gray-50 border border-gray-300 text-sm rounded-lg w-full p-2.5"}),
            "address": forms.Textarea(attrs={"class": "bg-gray-50 border border-gray-300 text-sm rounded-lg w-full p-2.5", "rows": 3}),
            "photo": forms.FileInput(attrs={"class": "bg-gray-50 border border-gray-300 text-sm rounded-lg w-full p-2.5", "accept": "image/*"}),
            "notes": forms.Textarea(attrs={"class": "bg-gray-50 border border-gray-300 text-sm rounded-lg w-full p-2.5", "rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].required = True
        # IMPORTANT: use model’s source of truth for choices
        self.fields["sex"].choices = [("", "Select...")] + list(Offender.SEX_CHOICES)

    def clean_age(self):
        age = self.cleaned_data.get("age")
        if age is not None and not (1 <= age <= 150):
            raise ValidationError("Age must be between 1 and 150.")
        return age

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get("date_of_birth")
        if dob:
            today = datetime.date.today()
            if dob > today:
                raise ValidationError("Date of birth cannot be in the future.")
            calc_age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if calc_age > 150:
                raise ValidationError("Date of birth seems unrealistic (>150 years old).")
        return dob

    def clean(self):
        cleaned = super().clean()
        age = cleaned.get("age")
        dob = cleaned.get("date_of_birth")
        if age and dob:
            today = datetime.date.today()
            calc = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if abs(calc - age) > 1:
                raise ValidationError(f"Age ({age}) and date of birth ({dob}) don't match (≈{calc}).")
        return cleaned

class OffenderSearchForm(forms.Form):
    search = forms.CharField(
        max_length=255, required=False,
        widget=forms.TextInput(attrs={"class": "bg-gray-50 border border-gray-300 text-sm rounded-lg w-full p-2.5",
                                      "placeholder": "Search name, occupation, notes..."}),
        label="",
    )
    sex = forms.ChoiceField(
        choices=[("", "Any Sex")] + list(Offender._meta.get_field("sex").choices),
        required=False,
        widget=forms.Select(attrs={"class": "bg-gray-50 border border-gray-300 text-sm rounded-lg w-full p-2.5"}),
        label="",
    )
    is_banned = forms.ChoiceField(
        choices=[("", "Any Status"), ("yes", "Currently Banned"), ("no", "Not Banned")],
        required=False,
        widget=forms.Select(attrs={"class": "bg-gray-50 border border-gray-300 text-sm rounded-lg w-full p-2.5"}),
        label="",
    )
