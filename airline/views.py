from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import View
from airline.models import Flight
from airline.services.user import UserService
from airline.services.plane import PlaneService
from airline.services.flight import FlightService
from home.forms import RegisterForm, LoginForm
from airline.forms import CreateFlightForm, UpdateFlightForm
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

def flight_administration(request):
    flights = FlightService.get_all()
    form = CreateFlightForm()
    form_errors = False

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "create":
            form = CreateFlightForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                new_flight = Flight(
                    origin=cd['origin'],
                    destination=cd['destination'],
                    departure_date=cd['departure_date'],
                    arrival_date=cd['arrival_date'],
                    duration=cd['arrival_date'] - cd['departure_date'],
                    base_price=cd['base_price'],
                    status=cd['status_id'],
                    plane=cd['plane_id'],
                )
                new_flight.save()
                return redirect('flight_administration')
            else:
                form_errors = True  # Marca que hay errores para mostrar el modal abierto

        elif action == "update":
            flight_id = request.POST.get("flight_id")
            flight_to_update = get_object_or_404(Flight, id=flight_id)
            update_form = UpdateFlightForm(request.POST)
            if update_form.is_valid():
                cd = update_form.cleaned_data
                flight_to_update.origin = cd['origin']
                flight_to_update.destination = cd['destination']
                flight_to_update.departure_date = cd['departure_date']
                flight_to_update.arrival_date = cd['arrival_date']
                flight_to_update.duration = cd['arrival_date'] - cd['departure_date']
                flight_to_update.base_price = cd['base_price']
                flight_to_update.status_id = cd['status_id']
                flight_to_update.plane_id = cd['plane_id']
                flight_to_update.save()
                return redirect('flight_administration')
            else:
                messages.error(request, "Error al actualizar el vuelo.")

        elif action == "delete":
            flight_id = request.POST.get("flight_id")
            if flight_id:
                try:
                    FlightService.delete(flight_id)
                    messages.success(request, "Vuelo eliminado correctamente.")
                except Exception:
                    messages.error(request, "Error al eliminar el vuelo.")
            else:
                messages.error(request, "No se indicó el ID del vuelo.")
            return redirect('flight_administration')

    update_form = []
    for flight in flights:
        uf = UpdateFlightForm(initial={
            'origin': flight.origin,
            'destination': flight.destination,
            'departure_date': flight.departure_date,
            'arrival_date': flight.arrival_date,
            'base_price': flight.base_price,
            'status_id': flight.status_id,
            'plane_id': flight.plane_id,
        })
        update_form.append((flight, uf))

    return render(request, 'flights/administration.html', {
        'flights': flights,
        'form': form,
        'form_errors': form_errors,
        'update_form': update_form,
    })

