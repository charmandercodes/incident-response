from django import forms
from .models import Incident
from a_offenders.models import Offender  # make sure this import matches your app

class IncidentForm(forms.ModelForm):
    # Explicitly define the offender dropdown
    offender = forms.ModelChoiceField(
        queryset=Offender.objects.all(),
        required=False,  # because your ForeignKey allows null
        widget=forms.Select(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                     'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 '
                     'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                     'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
        })
    )

    class Meta:
        model = Incident
        fields = [
            'title',
            'description',
            'incident_type',
            'venue',
            'offender',      # ForeignKey dropdown
            'offenders',     # ManyToMany (multi-select)
            'warning',
            'ban',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                         'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5',
                'placeholder': 'Enter incident title',
            }),
            'description': forms.Textarea(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                         'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5',
                'rows': 4,
                'placeholder': 'Describe the incident...',
            }),
            'venue': forms.Select(attrs={  # change to Select to get dropdown
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                         'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5',
            }),
            'offenders': forms.SelectMultiple(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                         'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 h-32',
            }),
            'warning': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5',
            }),
            'ban': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5',
            }),
        }
