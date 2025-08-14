from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from airline.models import User
from airline.services.user import UserService


# Formulario para registrar nuevos usuarios en el sistema
class RegisterForm(forms.Form):

    # Campo de texto para el nombre de usuario
    username = forms.CharField(
        max_length=150,
        label="Username",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    # Campo para ingresar la contraseña (oculta con PasswordInput)
    password1 = forms.CharField(
        max_length=128,
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    # Campo para repetir la contraseña y validar coincidencia
    password2 = forms.CharField(
        max_length=128,
        label="Repeat your password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    # Campo de correo electrónico
    email = forms.EmailField(
        label="Email", widget=forms.EmailInput(attrs={"class": "form-control"})
    )

    # Checkbox opcional para indicar si el usuario será administrador
    is_admin = forms.BooleanField(
        required=False,
        label="¿Es administrador?",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    # Validación individual del username
    def clean_username(self):
        username = self.cleaned_data["username"]
        # Verifica que el username no exista ya en la base de datos
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username has already been used")
        return username

    # Validación individual del email
    def clean_email(self):
        email = self.cleaned_data.get("email")
        # Verifica que el email no exista ya en la base de datos
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email has already been used")
        return email

    # Validación general del formulario
    def clean(self):
        cleaned_data = super().clean()
        pass1 = cleaned_data.get("password1")
        pass2 = cleaned_data.get("password2")
        # Verifica que las contraseñas coincidan
        if pass1 and pass2 and pass1 != pass2:
            raise ValidationError("Passwords do not match.")

    # Método para crear el usuario en la base de datos usando UserService
    def save(self):
        # Determina el rol según el checkbox
        role = "admin" if self.cleaned_data.get("is_admin") else "user"
        # Llama al servicio para crear el usuario con los datos ingresados
        return UserService.create(
            username=self.cleaned_data["username"],
            password=self.cleaned_data["password1"],
            email=self.cleaned_data["email"],
            role=role,
        )

# Formulario para iniciar sesión de usuarios en el sistema
class LoginForm(forms.Form):

    # Campo de texto para el nombre de usuario
    username = forms.CharField(
        label="Username",
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    # Campo de contraseña (oculta el texto ingresado)
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    # Validación general del formulario
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        # Verifica que existan ambos campos
        if username and password:
            # Autentica al usuario usando Django
            user = authenticate(username=username, password=password)
            # Si no se encuentra usuario con esas credenciales, lanza error
            if user is None:
                raise ValidationError("The username or password is incorrect.")
        return cleaned_data
