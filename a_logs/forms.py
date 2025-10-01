from django import forms

class LogFilterForm(forms.Form):
    ACTION_CHOICES = [
        ('', 'All Actions'),
        ('1', 'Added'),
        ('2', 'Changed'),
        ('3', 'Deleted'),
    ]
    
    username = forms.CharField(
        required=False,
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white',
            'placeholder': 'Enter username...',
        })
    )
    
    action_flag = forms.ChoiceField(
        required=False,
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
        })
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
        })
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        
        if not username:
            return username
        
        # Validation: Minimum length
        if len(username) < 2:
            raise forms.ValidationError("Username must be at least 2 characters long.")
        
        # Validation: Only allow alphanumeric, underscores, and hyphens
        import re
        if not re.match(r"^[a-zA-Z0-9_\-]+$", username):
            raise forms.ValidationError("Username can only contain letters, numbers, underscores, and hyphens.")
        
        return username
    
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        # Validation: date_from must be before date_to
        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError("Start date must be before end date.")
        
        return cleaned_data