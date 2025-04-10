from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth.forms import UserChangeForm
from .models import CustomUser

# Custom validator for username format
username_validator = RegexValidator(
    regex=r'^[a-z0-9]{3,30}$',
    message='Username must be 3-30 characters long and contain only lowercase letters and numbers.'
)

class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'first_name', 'last_name', 
                  'address', 'contact_number', 'state', 'state_code')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'state_code': forms.TextInput(attrs={'class': 'form-control'}),
        }

    username = forms.CharField(
        max_length=30,
        validators=[username_validator],
        help_text="Use only lowercase letters and numbers, 3-30 characters."
    )

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'first_name', 'last_name', 
                  'address', 'contact_number', 'state', 'state_code')