from django import forms
from django.core.exceptions import ValidationError
from .models import Offender
import datetime


class OffenderForm(forms.ModelForm):
    class Meta:
        model = Offender
        fields = [
            'name', 'contact_info', 'age', 'date_of_birth', 'sex',
            'height', 'weight', 'hair_color', 'eye_color', 
            'occupation', 'address', 'photo', 'notes'
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                         'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 '
                         'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                         'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'placeholder': 'Full name'
            }),
            'contact_info': forms.Textarea(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                         'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 '
                         'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                         'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'rows': 3,
                'placeholder': 'Phone, email, or other contact information'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                         'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 '
                         'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                         'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'min': 1,
                'max': 150,
                'placeholder': 'Age in years'
            }),
            'date_of_birth': forms.DateInput(attrs={
                 'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                         'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 '
                         'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                         'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'type': 'date'
            }),
            'sex': forms.Select(attrs={
                 'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                         'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 '
                         'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                         'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
            }),
            'height': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                         'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 '
                         'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                         'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'placeholder': "e.g., 5'10\", 178cm, 6 feet"
            }),
            'weight': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                         'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 '
                         'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                         'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'placeholder': 'e.g., 180lbs, 82kg'
            }),
            'hair_color': forms.TextInput(attrs={
                 'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                         'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 '
                         'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                         'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'placeholder': 'e.g., Brown, Black, Blonde, Gray'
            }),
            'eye_color': forms.TextInput(attrs={
                 'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                         'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 '
                         'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                         'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'placeholder': 'e.g., Brown, Blue, Green, Hazel'
            }),
            'occupation': forms.TextInput(attrs={
                  'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                         'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 '
                         'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                         'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'placeholder': 'Job title or profession'
            }),
            'address': forms.Textarea(attrs={
                 'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                         'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 '
                         'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                         'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'rows': 3,
                'placeholder': 'Full address including city, state, zip'
            }),
            'photo': forms.FileInput(attrs={
                 'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                         'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 '
                         'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                         'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'accept': 'image/*'
            }),
            'notes': forms.Textarea(attrs={
                  'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                         'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 '
                         'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                         'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'rows': 4,
                'placeholder': 'Additional observations, distinguishing marks, behavioral notes, etc.'
            }),
        }
        
        labels = {
            'name': 'Full Name',
            'contact_info': 'Contact Information',
            'age': 'Age',
            'date_of_birth': 'Date of Birth',
            'sex': 'Sex',
            'height': 'Height',
            'weight': 'Weight',
            'hair_color': 'Hair Color',
            'eye_color': 'Eye Color',
            'occupation': 'Occupation',
            'address': 'Address',
            'photo': 'Photo',
            'notes': 'Additional Notes',
        }
        
        help_texts = {
            'age': 'Enter age in years (optional if date of birth is provided)',
            'date_of_birth': 'Optional if age is provided',
            'height': 'Any format acceptable (feet/inches, cm, etc.)',
            'weight': 'Any format acceptable (lbs, kg, etc.)',
            'photo': 'Upload a photo (JPG, PNG, GIF accepted)',
            'notes': 'Any additional information that might be relevant for identification or incidents',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make name field required
        self.fields['name'].required = True
        
        # Add empty option for sex field
        sex_choices = [('', 'Select...')] + list(self.fields['sex'].choices)
        self.fields['sex'].choices = sex_choices

    def clean(self):
        cleaned_data = super().clean()
        age = cleaned_data.get('age')
        date_of_birth = cleaned_data.get('date_of_birth')
        
        # Validate that at least one of age or date_of_birth is provided
        if not age and not date_of_birth:
            # This is just a warning, not a hard requirement
            pass
        
        # If both are provided, check for consistency
        if age and date_of_birth:
            today = datetime.date.today()
            calculated_age = today.year - date_of_birth.year
            if today.month < date_of_birth.month or (today.month == date_of_birth.month and today.day < date_of_birth.day):
                calculated_age -= 1
            
            # Allow for some flexibility (±1 year) in case of birthdays
            if abs(calculated_age - age) > 1:
                raise ValidationError(
                    f"Age ({age}) and date of birth ({date_of_birth}) don't match. "
                    f"Calculated age from DOB is {calculated_age}."
                )
        
        return cleaned_data

    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get('date_of_birth')
        if date_of_birth:
            today = datetime.date.today()
            if date_of_birth > today:
                raise ValidationError("Date of birth cannot be in the future.")
            
            # Check for reasonable age limits (e.g., not older than 150)
            age = today.year - date_of_birth.year
            if today.month < date_of_birth.month or (today.month == date_of_birth.month and today.day < date_of_birth.day):
                age -= 1
            
            if age > 150:
                raise ValidationError("Date of birth seems unrealistic (person would be over 150 years old).")
                
        return date_of_birth

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is not None:
            if age < 1 or age > 150:
                raise ValidationError("Age must be between 1 and 150.")
        return age

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            # Check file size (limit to 5MB)
            if photo.size > 5 * 1024 * 1024:
                raise ValidationError("Photo size cannot exceed 5MB.")
            
            # Check file type
            if not photo.content_type.startswith('image/'):
                raise ValidationError("Please upload a valid image file.")
                
        return photo


class OffenderSearchForm(forms.Form):
    """Simple search form for filtering offenders"""
    search = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                     'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 '
                     'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                     'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
            'placeholder': 'Search by name, occupation, or notes...'
        })
    )
    
    sex = forms.ChoiceField(
        choices=[('', 'Any Sex')] + Offender._meta.get_field('sex').choices,
        required=False,
        widget=forms.Select(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                     'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 '
                     'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                     'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'
        })
    )
    
    is_banned = forms.ChoiceField(
        choices=[
            ('', 'Any Status'),
            ('yes', 'Currently Banned'),
            ('no', 'Not Banned')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                     'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 '
                     'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                     'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'
        }),
        label='Ban Status'
    )