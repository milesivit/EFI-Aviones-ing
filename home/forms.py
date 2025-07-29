from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from airline.models import User
from airline.services.user import UserService

class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label="Username",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        max_length=128,
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        max_length=128,
        label="Repeat your password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    is_admin = forms.BooleanField(
        required=False,
        label="¿Es administrador?",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username has already been used")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email has already been used")
        return email

    def clean(self):
        cleaned_data = super().clean()
        pass1 = cleaned_data.get("password1")
        pass2 = cleaned_data.get("password2")
        if pass1 and pass2 and pass1 != pass2:
            raise ValidationError("Passwords do not match.")

    def save(self):
        role = 'admin' if self.cleaned_data.get('is_admin') else 'user'
        return UserService.create(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password1'],
            email=self.cleaned_data['email'],
            role=role
        )

class LoginForm(forms.Form):
    username=forms.CharField(
        label="Username",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                'class' : 'form-control'
            }
        )
    )
    password=forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise ValidationError("The username or password is incorrect.")
        return cleaned_data
