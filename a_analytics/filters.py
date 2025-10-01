# a_analytics/filters.py
import django_filters
from django import forms
from a_incidents.models import Incident


class IncidentFilter(django_filters.FilterSet):
    offender_name = django_filters.CharFilter(
        field_name='offender__name',
        lookup_expr='icontains',
        label='Filter by Offender Name',
        widget=forms.TextInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white',
            'placeholder': 'Enter offender name...',
            'maxlength': '100',
        })
    )
    
    class Meta:
        model = Incident
        fields = ['offender_name']