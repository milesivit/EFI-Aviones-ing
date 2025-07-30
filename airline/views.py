from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import View
from airline.services.user import UserService
from airline.services.plane import PlaneService
from airline.services.flight import FlightService
from home.forms import RegisterForm, LoginForm
from django.contrib.auth import authenticate, login

# Función para listar aviones
def plane_list(request):
    airplanes = PlaneService.get_all()  
    return render(request, 'plane/list.html', {'airplanes': airplanes})

# --------------------------------------------------------------------USUARIOS
# Función para listar usuarios
def user_list(request):
    users = UserService.get_all()
    return render(request, 'users/list.html', {'users': users})

# Registrar un nuevo usuario
# segun las buenas practicas para las password va desde el modelo, repositorio, service, form y luego la view con su respectiva url
def user_register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # guardás y obtenés el objeto usuario
            login(request, user)  # iniciás sesión automáticamente
            messages.success(request, "Usuario creado correctamente.")
            return redirect('index')
        else: #sino error
            messages.error(request, "Por favor corrige los errores del formulario.")
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenido/a {user.username}")
                return redirect('index')  # Cambia 'index' por la vista que desees como home/logueado
            else:
                messages.error(request, "Credenciales inválidas. Intenta nuevamente.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})

def flight_list(request):
    flights = FlightService.get_all()
    return render(request, 'flights/list.html', {'flights': flights})