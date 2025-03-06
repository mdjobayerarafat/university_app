from django import forms
from django.utils import timezone
from .models import Event, EventRSVP

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title',
            'description',
            'start_datetime',
            'end_datetime',
            'location',
            'image',
            'is_university_wide',
            'max_participants',
            'tags'
        ]
        widgets = {
            'start_datetime': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'end_datetime': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'description': forms.Textarea(attrs={'rows': 4}),
            'tags': forms.TextInput(attrs={'placeholder': 'Enter tags separated by commas'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_datetime = cleaned_data.get('start_datetime')
        end_datetime = cleaned_data.get('end_datetime')
        now = timezone.now()

        if start_datetime and start_datetime < now:
            raise forms.ValidationError('Start time cannot be in the past.')

        if start_datetime and end_datetime and end_datetime <= start_datetime:
            raise forms.ValidationError('End time must be after start time.')

        # Convert tags string to list
        tags = cleaned_data.get('tags')
        if isinstance(tags, str):
            cleaned_data['tags'] = [tag.strip() for tag in tags.split(',') if tag.strip()]

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

        # Make certain fields required
        self.fields['title'].required = True
        self.fields['start_datetime'].required = True
        self.fields['end_datetime'].required = True
        self.fields['location'].required = True

        # Add help texts
        self.fields['tags'].help_text = 'Enter tags separated by commas (e.g., sports, academic, social)'
        self.fields['max_participants'].help_text = 'Leave blank for unlimited participants'
        self.fields['is_university_wide'].help_text = 'Check if this event is open to all university students'


class EventRSVPForm(forms.ModelForm):
    class Meta:
        model = EventRSVP
        fields = ['status']
        widgets = {
            'status': forms.Select(
                attrs={'class': 'form-control'},
                choices=[
                    ('going', 'Going'),
                    ('maybe', 'Maybe'),
                    ('not_going', 'Not Going')
                ]
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].label = 'RSVP Status'