from django import forms
from django.core.validators import RegexValidator
from .models import Booking

class BookingForm(forms.ModelForm):
    phone = forms.CharField(
        max_length=10,
        validators=[RegexValidator(
            regex=r'^[6-9]\d{9}$',
            message="Enter a valid 10-digit mobile number starting with 6-9.",
            code='invalid_mobile'
        )],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'})
    )

    class Meta:
        model = Booking
        fields = ['phone', 'address', 'date', 'time']
        widgets = {
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your address', 'rows': 3}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }
