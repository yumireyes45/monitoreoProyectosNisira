from django.forms import forms
from .models import Project, Phase, Cost
from django import forms

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'total_budget', 'start_date', 'end_date']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'block w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500',
            }),
            'description': forms.Textarea(attrs={
                'class': 'block w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500', 
                'rows': 3
            }),
            'total_budget': forms.NumberInput(attrs={
                'class': 'block w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500',
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'block w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500', 
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'block w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500', 
                'type': 'date'
            }),
        }

        
class PhaseForm(forms.ModelForm):
    class Meta:
        model = Phase
        fields = ['project', 'name', 'start_date', 'end_date', 'important', 'status', 'percentage_completed', 'duration_hours', 'user']
        widgets = {
            'project': forms.Select(attrs={'class': 'w-full mt-1 p-3 border border-gray-300 rounded focus:ring focus:ring-indigo-200 focus:border-indigo-300'}),
            'name': forms.TextInput(attrs={'class': 'block w-full mt-1 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'}),
            'start_date': forms.DateInput(attrs={'class': 'block w-full mt-1 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-200 focus:ring-opacity-50', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'block w-full mt-1 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-200 focus:ring-opacity-50', 'type': 'date'}),
            'important': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500'}),
            'status': forms.Select(attrs={'class': 'w-full mt-1 p-3 border border-gray-300 rounded focus:ring focus:ring-indigo-200 focus:border-indigo-300'}),
            'percentage_completed': forms.NumberInput(attrs={'class': 'block w-full mt-1 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-200 focus:ring-opacity-50', 'step': '0.01'}),
            'duration_hours': forms.NumberInput(attrs={'class': 'block w-full mt-1 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'}),
            'user': forms.Select(attrs={'class': 'w-full mt-1 p-3 border border-gray-300 rounded focus:ring focus:ring-indigo-200 focus:border-indigo-300'}),
        }

class CostForm(forms.ModelForm):
    class Meta:
        model = Cost
        fields = ['project', 'phase', 'date', 'description', 'amount', 'user']
        widgets = {
            'project': forms.Select(attrs={'class': 'w-full mt-1 p-3 border border-gray-300 rounded focus:ring focus:ring-indigo-200 focus:border-indigo-300'}),
            'phase': forms.Select(attrs={'class': 'w-full mt-1 p-3 border border-gray-300 rounded focus:ring focus:ring-indigo-200 focus:border-indigo-300'}),
            'date': forms.DateInput(attrs={'class': 'w-full mt-1 p-3 border border-gray-300 rounded focus:ring focus:ring-indigo-200 focus:border-indigo-300', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'w-full mt-1 p-3 border border-gray-300 rounded focus:ring focus:ring-indigo-200 focus:border-indigo-300'}),
            'amount': forms.NumberInput(attrs={'class': 'w-full mt-1 p-3 border border-gray-300 rounded focus:ring focus:ring-indigo-200 focus:border-indigo-300'}),
            'user': forms.Select(attrs={'class': 'w-full mt-1 p-3 border border-gray-300 rounded focus:ring focus:ring-indigo-200 focus:border-indigo-300'}),
        }

        project = forms.ModelChoiceField(queryset=Project.objects.all())
        phase = forms.ModelChoiceField(queryset=Phase.objects.all())
