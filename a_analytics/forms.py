# a_analytics/forms.py
from django import forms
import re

class OffenderFilterForm(forms.Form):
    offender_name = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white',
            'placeholder': 'Enter offender name...',
        })
    )
    
    def clean_offender_name(self):
        name = self.cleaned_data.get('offender_name', '').strip()
        
        if not name:
            return name
        
        # Validation 1: Minimum length
        if len(name) < 2:
            raise forms.ValidationError("Offender name must be at least 2 characters long.")
        
        # Validation 2: Invalid characters
        if not re.match(r"^[a-zA-Z\s\-']+$", name):
            raise forms.ValidationError("Invalid characters in offender name. Please use only letters, spaces, hyphens, and apostrophes.")
        
        # Validation 3: SQL injection attempts
        if any(keyword in name.lower() for keyword in ['select', 'drop', 'delete', 'insert', 'update', '--', ';', '/*']):
            raise forms.ValidationError("Invalid input detected. Please enter a valid offender name.")
        
        return name