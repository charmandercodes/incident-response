from django import forms
from .models import Venue

AUS_STATE_CHOICES = [
    ('ACT', 'Australian Capital Territory'),
    ('NSW', 'New South Wales'),
    ('NT', 'Northern Territory'),
    ('QLD', 'Queensland'),
    ('SA', 'South Australia'),
    ('TAS', 'Tasmania'),
    ('VIC', 'Victoria'),
    ('WA', 'Western Australia'),
]

class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = [
            'name', 'description', 'address', 'city', 'state', 'postal_code',
            'phone', 'email', 'manager_name', 'venue_type', 'capacity', 
            'operating_hours', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                         'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 '
                         'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                         'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'placeholder': 'Enter venue name',
            }),
            'description': forms.Textarea(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                         'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 '
                         'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                         'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'rows': 3,
                'placeholder': 'Venue description (optional)...',
            }),
            'address': forms.Textarea(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                         'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 '
                         'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                         'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'rows': 2,
                'placeholder': 'Enter full address',
            }),
            'city': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                         'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 '
                         'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                         'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'placeholder': 'City',
            }),
            'state': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                         'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 '
                         'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                         'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
            }, choices=AUS_STATE_CHOICES),
            'postal_code': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                         'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 '
                         'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                         'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'placeholder': 'Postal Code',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                         'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 '
                         'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                         'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'placeholder': 'Phone number (optional)',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                         'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 '
                         'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                         'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'placeholder': 'Email address (optional)',
            }),
            'manager_name': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                         'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 '
                         'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                         'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'placeholder': 'Manager name (optional)',
            }),
            'venue_type': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                         'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 '
                         'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                         'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                         'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 '
                         'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                         'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'placeholder': 'Maximum occupancy (optional)',
            }),
            'operating_hours': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg '
                         'focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 '
                         'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                         'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'placeholder': 'e.g., Mon-Sun 9AM-9PM',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600',
            }),
        }

    def clean_capacity(self):
        capacity = self.cleaned_data.get('capacity')
        if capacity is not None and capacity < 0:
            raise forms.ValidationError("Capacity cannot be negative.")
        return capacity

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code')
        if postal_code and not postal_code.isalnum():
            raise forms.ValidationError("Postal code must be alphanumeric.")
        return postal_code
