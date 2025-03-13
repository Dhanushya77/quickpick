# from django import forms
# from django.core.validators import RegexValidator
# from .models import Booking

# class BookingForm(forms.ModelForm):
#     phone = forms.CharField(
#         max_length=10,
#         validators=[RegexValidator(
#             regex=r'^[6-9]\d{9}$',
#             message="Enter a valid 10-digit mobile number starting with 6-9.",
#             code='invalid_mobile'
#         )],
#         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'})
#     )

#     new_address = forms.CharField(required=False, label="New Address", 
#                                    widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter new address', 'rows': 3}))
    
#     new_phone = forms.CharField(required=False, label="New Phone Number", 
#                                  widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter new phone number'}))

#     class Meta:
#         model = Booking
#         fields = ['phone', 'address', 'date', 'time']
#         widgets = {
#             'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your address', 'rows': 3}),
#             'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
#             'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
#         }


from django import forms
from django.core.validators import RegexValidator
from .models import *

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
    
    address = forms.ModelChoiceField(
        queryset=Address.objects.none(),  
        empty_label="Select an existing address",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    new_address = forms.CharField(required=False, label="New Address", 
                                   widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter new address', 'rows': 3}))
    
    new_phone = forms.CharField(required=False, label="New Phone Number", 
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter new phone number'}))

    class Meta:
        model = Booking
        fields = ['phone', 'address', 'date', 'time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        address = cleaned_data.get('address')
        new_address = cleaned_data.get('new_address')
        phone = cleaned_data.get('phone')
        new_phone = cleaned_data.get('new_phone')

        # Validate address selection
        if not address and not new_address:
            raise forms.ValidationError("You must provide either an existing address or a new address.")
        
        if new_address and address:
            raise forms.ValidationError("Please provide either a new address or select an existing address, not both.")

        # Validate phone selection
        if not phone and not new_phone:
            raise forms.ValidationError("You must provide either an existing phone number or a new phone number.")
        
        if phone and new_phone:
            raise forms.ValidationError("Please provide either a new phone number or select an existing phone number, not both.")

        return cleaned_data