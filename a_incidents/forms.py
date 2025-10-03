from django import forms
from .models import Incident


class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ["title", "description", "venue", "offender_name", "warning", "ban", "severity"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5 "
                             "dark:bg-gray-700 dark:border-gray-600 dark:text-white",
                    "placeholder": "Enter incident title",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5 "
                             "dark:bg-gray-700 dark:border-gray-600 dark:text-white",
                    "rows": 4,
                    "placeholder": "Describe the incident...",
                }
            ),
            "venue": forms.TextInput(
                attrs={
                    "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5 "
                             "dark:bg-gray-700 dark:border-gray-600 dark:text-white",
                    "placeholder": "Enter venue name",
                }
            ),
            "offender_name": forms.TextInput(
                attrs={
                    "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5 "
                             "dark:bg-gray-700 dark:border-gray-600 dark:text-white",
                    "placeholder": "Enter offender name",
                }
            ),
            "warning": forms.Select(
                attrs={"class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5 "
                                "dark:bg-gray-700 dark:border-gray-600 dark:text-white"}
            ),
            "ban": forms.Select(
                attrs={"class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5 "
                                "dark:bg-gray-700 dark:border-gray-600 dark:text-white"}
            ),
            "severity": forms.Select(
                attrs={"class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5 "
                                "dark:bg-gray-700 dark:border-gray-600 dark:text-white"}
            ),
        }
