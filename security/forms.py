from django import forms
from .models import Report

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['report_type', 'title', 'description', 'location',
                 'date_occurred', 'image', 'is_urgent']
        widgets = {
            'date_occurred': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class UpdateReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['status']