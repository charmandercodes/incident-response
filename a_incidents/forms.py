from django import forms
from .models import Incident
from a_offenders.models import Offender
from a_venues.models import Venue

class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['title', 'description', 'venue', 'incident_type', 'offender', 'offenders', 'warning', 'ban']
        
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
            'venue': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5',
            }),
            'incident_type': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5',
            }),
            'offender': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5',
            }),
            'offenders': forms.SelectMultiple(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5',
            }),
            'warning': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5',
            }),
            'ban': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['venue'].queryset = Venue.objects.all().order_by('name')
        self.fields['offender'].queryset = Offender.objects.all().order_by('name')
        self.fields['offenders'].queryset = Offender.objects.all().order_by('name')
