# a_logs/filters.py
import django_filters
from django.contrib.admin.models import LogEntry
from django import forms


class LogEntryFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(
        field_name='user__username',
        lookup_expr='iexact',  # Changed from 'icontains' to 'iexact'
        label='Username',
        widget=forms.TextInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white',
            'placeholder': 'Enter exact username...',
        })
    )
    
    action_flag = django_filters.ChoiceFilter(
        choices=[
            ('', 'All Actions'),
            ('1', 'Added'),
            ('2', 'Changed'),
            ('3', 'Deleted'),
        ],
        label='Action Type',
        empty_label=None,
        widget=forms.Select(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
        })
    )
    
    date_from = django_filters.DateFilter(
        field_name='action_time',
        lookup_expr='gte',
        label='From Date',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
        })
    )
    
    date_to = django_filters.DateFilter(
        field_name='action_time',
        lookup_expr='lte',
        label='To Date',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
        })
    )
    
    class Meta:
        model = LogEntry
        fields = ['username', 'action_flag', 'date_from', 'date_to']