# forms.py
from django import forms
from .models import Booking
from django.contrib.auth.forms import SetPasswordForm

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['car_owner_name', 'brand', 'model', 'variant', 'email', 'phone', 'address1', 'address2', 'city', 'state', 'zip', 'inspection_date', 'message']
        widgets = {
            'inspection_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(BookingForm, self).__init__(*args, **kwargs)
        self.fields['car_owner_name'].required = True
        self.fields['brand'].required = True
        self.fields['model'].required = True
        self.fields['variant'].required = True
        self.fields['email'].required = True
        self.fields['phone'].required = True
        self.fields['address1'].required = True
        self.fields['address2'].required = True
        self.fields['city'].required = True
        self.fields['state'].required = True
        self.fields['zip'].required = True
        self.fields['inspection_date'].required = True
        self.fields['message'].required = False

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label=("New password"),
        widget=forms.PasswordInput,
        strip=False,
    )
    new_password2 = forms.CharField(
        label=("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput,
    )
