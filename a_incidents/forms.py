from django import forms
from .models import Incident

class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                         'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 '
                         'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                         'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'placeholder': 'Enter incident title',
            }),
            'description': forms.Textarea(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                         'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 '
                         'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                         'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'rows': 4,
                'placeholder': 'Describe the incident...',
            }),
        }
