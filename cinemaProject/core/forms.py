from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
import re
from core.constants import RE_PATTERN

User = get_user_model()


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})


class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget = forms.TextInput(attrs={
            'class': 'form-control ',
            'placeholder': 'Create your username'
        })
        self.fields['email'].widget = forms.EmailInput(attrs={
            'class': 'form-control ',
            'placeholder': 'Enter your email'
        })
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'form-control ',
            'placeholder': 'Create password'
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'form-control ',
            'placeholder': 'Repeat your password'
        })

    class Meta:
        model = User
        fields = ('username', 'email',)

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if re.match(RE_PATTERN, email) is None:
            raise forms.ValidationError("Invalid email")

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("User with this email already exists")

        return email
