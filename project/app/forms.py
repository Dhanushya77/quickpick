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
from .models import Booking, Address

class BookingForm(forms.ModelForm):
    phone = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    new_phone = forms.CharField(
        required=False, 
        label="New Phone Number", 
        validators=[RegexValidator(
            regex=r'^[6-9]\d{9}$',
            message="Enter a valid 10-digit mobile number starting with 6-9.",
            code='invalid_mobile'
        )],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter new phone number'})
    )

    address = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    new_address = forms.CharField(
        required=False, 
        label="New Address", 
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter new address', 'rows': 3})
    )

    class Meta:
        model = Booking
        fields = ['phone', 'address', 'date', 'time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  
        super().__init__(*args, **kwargs)
        
        if user:
            
            user_addresses = Address.objects.filter(user=user)
            address_choices = [(addr.id, f"{addr.address_line}") for addr in user_addresses]
            address_choices.insert(0, ('', 'Select an address (or enter a new one)'))
            self.fields['address'].choices = address_choices

            phone_choices = [(addr.phone_number, addr.phone_number) for addr in user_addresses]
            phone_choices.insert(0, ('', 'Select a phone number (or enter a new one)'))
            self.fields['phone'].choices = phone_choices

    def clean(self):
        cleaned_data = super().clean()
        phone = cleaned_data.get('phone')
        new_phone = cleaned_data.get('new_phone')
        address = cleaned_data.get('address')
        new_address = cleaned_data.get('new_address')

        if not phone and not new_phone:
            raise forms.ValidationError("Please select an existing phone number or enter a new one.")

        if not address and not new_address:
            raise forms.ValidationError("Please select an existing address or enter a new one.")

        return cleaned_data
