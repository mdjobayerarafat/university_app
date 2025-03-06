from django import forms

from academics.models import Department, ClassSection
from .models import Notification, NotificationPreference


class NotificationForm(forms.Form):
    type = forms.ChoiceField(
        choices=Notification.TYPES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
    )
    priority = forms.ChoiceField(
        choices=Notification.PRIORITIES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    action_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )
    target_type = forms.ChoiceField(
        choices=[
            ('all', 'All Users'),
            ('department', 'Specific Department'),
            ('section', 'Specific Class Section'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label="Select Department",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    section = forms.ModelChoiceField(
        queryset=ClassSection.objects.none(),
        required=False,
        empty_label="Select Class Section",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        target_type = cleaned_data.get('target_type')
        department = cleaned_data.get('department')
        section = cleaned_data.get('section')

        if target_type == 'department' and not department:
            raise forms.ValidationError('Please select a department.')
        elif target_type == 'section' and not section:
            raise forms.ValidationError('Please select a class section.')

        return cleaned_data
class NotificationPreferenceForm(forms.ModelForm):
    class Meta:
        model = NotificationPreference
        fields = ['email_enabled', 'push_enabled', 'sms_enabled',
                 'quiet_hours_start', 'quiet_hours_end']
        widgets = {
            'quiet_hours_start': forms.TimeInput(
                attrs={'type': 'time', 'class': 'form-control'}
            ),
            'quiet_hours_end': forms.TimeInput(
                attrs={'type': 'time', 'class': 'form-control'}
            ),
            'email_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'push_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sms_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }