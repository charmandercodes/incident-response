# a_offenders/forms.py
from django import forms
from django.core.exceptions import ValidationError
import datetime
from .models import Offender, SEVERITY
from a_venues.models import Venue


class OffenderForm(forms.ModelForm):
    # --- Quick actions ---
    warning_now = forms.BooleanField(required=False, label="Create a Warning now?")
    warning_severity = forms.ChoiceField(
        required=False,
        choices=SEVERITY,
        label="Warning Severity",
    )

    ban_now = forms.BooleanField(required=False, label="Create a Ban now?")
    ban_duration = forms.ChoiceField(
        required=False,
        choices=[
            ("", "N/A"),
            ("1", "1 day"),
            ("3", "3 days"),
            ("7", "1 week"),
            ("14", "2 weeks"),
            ("30", "1 month"),
            ("90", "3 months"),
            ("365", "1 year"),
            ("permanent", "Permanent"),
        ],
        label="Ban Duration",
    )
    ban_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        label="Ban Reason",
    )

    # --- U128: notify venue on ban ---
    notify_venue = forms.BooleanField(
        required=False,
        label="Email the venue about this ban?",
    )
    # set queryset at runtime in __init__ to avoid import-time evaluation
    venue_to_notify = forms.ModelChoiceField(
        required=False,
        queryset=Venue.objects.none(),
        label="Venue to notify",
        widget=forms.Select(
            attrs={
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg "
                    "focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 "
                    "dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                )
            }
        ),
        help_text="We’ll use the email saved on this venue.",
    )

    class Meta:
        model = Offender
        fields = [
            "name",
            "contact_info",
            "age",
            "date_of_birth",
            "sex",
            "height",
            "weight",
            "hair_color",
            "eye_color",
            "occupation",
            "address",
            "photo",
            "notes",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": (
                        "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg "
                        "focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
                    ),
                    "placeholder": "Enter full name",
                }
            ),
            "contact_info": forms.Textarea(
                attrs={
                    "class": (
                        "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg "
                        "focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
                    ),
                    "rows": 3,
                    "placeholder": "Phone, email, or other contact details (optional)",
                }
            ),
            "photo": forms.ClearableFileInput(
                attrs={
                    "class": (
                        "block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer "
                        "bg-gray-50 dark:text-gray-400 focus:outline-none"
                    )
                }
            ),
            "age": forms.NumberInput(
                attrs={
                    "class": (
                        "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg "
                        "focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
                    ),
                    "placeholder": "Age",
                }
            ),
            "date_of_birth": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": (
                        "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg "
                        "focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
                    ),
                }
            ),
            "sex": forms.Select(
                attrs={
                    "class": (
                        "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg "
                        "focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
                    )
                }
            ),
            "height": forms.TextInput(
                attrs={
                    "class": (
                        "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg "
                        "focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
                    ),
                    "placeholder": "Height (e.g., 170cm)",
                }
            ),
            "weight": forms.TextInput(
                attrs={
                    "class": (
                        "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg "
                        "focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
                    ),
                    "placeholder": "Weight (e.g., 65kg)",
                }
            ),
            "hair_color": forms.TextInput(
                attrs={
                    "class": (
                        "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg "
                        "focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
                    ),
                    "placeholder": "Hair color",
                }
            ),
            "eye_color": forms.TextInput(
                attrs={
                    "class": (
                        "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg "
                        "focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
                    ),
                    "placeholder": "Eye color",
                }
            ),
            "occupation": forms.TextInput(
                attrs={
                    "class": (
                        "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg "
                        "focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
                    ),
                    "placeholder": "Occupation (optional)",
                }
            ),
            "address": forms.Textarea(
                attrs={
                    "class": (
                        "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg "
                        "focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
                    ),
                    "rows": 2,
                    "placeholder": "Address",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": (
                        "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg "
                        "focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
                    ),
                    "rows": 3,
                    "placeholder": "Additional notes (optional)",
                }
            ),
        }

    # -------- lifecycle --------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # required/choices polish
        self.fields["name"].required = True
        self.fields["sex"].choices = [("", "Select...")] + list(Offender.SEX_CHOICES)

        # runtime queryset (prevents import-time DB work and eases testing)
        self.fields["venue_to_notify"].queryset = Venue.objects.order_by("name")

    # -------- field-level validation --------
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
            calc_age = today.year - dob.year - (
                (today.month, today.day) < (dob.month, dob.day)
            )
            if calc_age > 150:
                raise ValidationError("Date of birth seems unrealistic (>150 years old).")
        return dob

    # -------- form-level validation --------
    def clean(self):
        cleaned = super().clean()

        # link age <-> dob sanity
        age = cleaned.get("age")
        dob = cleaned.get("date_of_birth")
        if age and dob:
            today = datetime.date.today()
            calc = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if abs(calc - age) > 1:
                # attach errors to fields so the form highlights them properly
                self.add_error("age", f"Age and date of birth don’t match (calculated ~{calc}).")
                self.add_error("date_of_birth", "Check the date or the age value.")

        # U128: if user wants to notify, venue is required
        if cleaned.get("notify_venue") and not cleaned.get("venue_to_notify"):
            self.add_error("venue_to_notify", "Select a venue to notify.")

        return cleaned


class OffenderSearchForm(forms.Form):
    search = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "bg-gray-50 border border-gray-300 text-sm rounded-lg w-full p-2.5",
                "placeholder": "Search name, occupation, notes...",
            }
        ),
        label="",
    )
    sex = forms.ChoiceField(
        choices=[("", "Any Sex")] + list(Offender._meta.get_field("sex").choices),
        required=False,
        widget=forms.Select(
            attrs={"class": "bg-gray-50 border border-gray-300 text-sm rounded-lg w-full p-2.5"}
        ),
        label="",
    )
    is_banned = forms.ChoiceField(
        choices=[("", "Any Status"), ("yes", "Currently Banned"), ("no", "Not Banned")],
        required=False,
        widget=forms.Select(
            attrs={"class": "bg-gray-50 border border-gray-300 text-sm rounded-lg w-full p-2.5"}
        ),
        label="",
    )
