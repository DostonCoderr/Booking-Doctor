from django import forms
from .models import Appointment, Patient, MedicalRecord, UserProfile, Review
from django.conf import settings
from django.utils import timezone

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bugungi sanani minimal sana sifatida o'rnatish
        self.fields['date'].widget.attrs['min'] = timezone.now().date().isoformat()
        # Agar form bo'sh bo'lsa, bugungi sanani default qiymat sifatida o'rnatish
        if 'initial' not in kwargs or not kwargs['initial'].get('date'):
            self.fields['date'].initial = timezone.now().date().isoformat()

class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['diagnosis', 'test_results', 'examination_notes']
        widgets = {
            'diagnosis': forms.Textarea(attrs={'rows': 5}),
            'test_results': forms.Textarea(attrs={'rows': 5}),
            'examination_notes': forms.Textarea(attrs={'rows': 5}),
        }

class UserProfileForm(forms.ModelForm):
    languages = forms.ChoiceField(choices=settings.LANGUAGES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = UserProfile
        fields = ['name', 'age', 'photo', 'theme', 'email', 'phone', 'languages']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'theme': forms.Select(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['comment', 'rating']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'rating': forms.Select(attrs={'class': 'form-control'}),
        }