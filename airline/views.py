# Importaciones de terceros (librerías instaladas, en este caso Django)
import string
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth import authenticate, login

# Importaciones internas de la aplicación (modelos, servicios y formularios)
from airline.models import Flight, Plane
from airline.services.user import UserService
from airline.services.plane import PlaneService
from airline.services.flight import FlightService
from airline.forms import CreateFlightForm, UpdateFlightForm, CreatePlaneForm, UpdatePlaneForm  # Agregá UpdatePlaneForm si no lo tenés
from home.forms import RegisterForm, LoginForm


# --------------------------------------------------------------------
# Función para listar aviones y manejar creación, actualización y eliminación
def plane_list(request):
    airplanes = PlaneService.get_all()  

    form = CreatePlaneForm()
    form_errors = False
    update_errors = False
    update_form_with_errors = None
    update_plane_id = None

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "create":
            form = CreatePlaneForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                new_plane = Plane(
                    model=cd['model'],
                    capacity=cd['capacity'],
                    rows=cd['rows'],
                    columns=cd['columns'],
                )
                new_plane.save()
                return redirect('plane_list')
            else:
                form_errors = True
        
        elif action == "update":
            update_plane_id = request.POST.get("plane_id")
            plane_to_update = get_object_or_404(Plane, id=update_plane_id)
            update_form_with_errors = UpdatePlaneForm(request.POST, plane_id=plane_to_update.id)
            if update_form_with_errors.is_valid():
                # Guardar los cambios manualmente, porque es un forms.Form
                cd = update_form_with_errors.cleaned_data
                plane_to_update.model = cd['model']
                plane_to_update.capacity = cd['capacity']
                plane_to_update.rows = cd['rows']
                plane_to_update.columns = cd['columns']
                plane_to_update.save()
                return redirect('plane_list')
            else:
                update_errors = True
        
        elif action == "delete":
            plane_id = request.POST.get("plane_id")
            if plane_id:
                try:
                    PlaneService.delete(plane_id)
                    messages.success(request, "Avión eliminado correctamente.")
                except Exception:
                    messages.error(request, "Error al eliminar el avión.")
            else:
                messages.error(request, "No se indicó el ID del avión.")
            return redirect('plane_list')

    update_form = []
    for plane in airplanes:
        if update_errors and str(plane.id) == str(update_plane_id):
            uf = update_form_with_errors
        else:
            uf = UpdatePlaneForm(
                initial={
                    'model': plane.model,
                    'capacity': plane.capacity,
                    'rows': plane.rows,
                    'columns': plane.columns,
                },
                plane_id=plane.id
            )
        update_form.append((plane, uf))

    return render(request, 'plane/list.html', {
        'airplanes': airplanes,
        'form': form,
        'form_errors': form_errors,
        'update_form': update_form,
        'update_errors': update_errors,
        'update_plane_id': update_plane_id,
    })


    # Renderizamos plantilla con todos los datos y formularios
    return render(request, 'plane/list.html', {
        'airplanes': airplanes,
        'form': form,
        'form_errors': form_errors,
        'update_form': update_form,
        'update_errors': update_errors,
        'update_plane_id': update_plane_id,
    })


# --------------------------------------------------------------------
# Función para detalle y layout dinámico de asientos del avión (sin cambios)
def plane_detail(request, plane_id):
    plane = get_object_or_404(Plane, pk=plane_id)
    rows = plane.rows
    cols = plane.columns

    column_letters = string.ascii_uppercase[:cols]
    seat_matrix = []

    # 🧠 Dividir columnas en bloques balanceados (máximo 3 bloques)
    max_bloques = 3
    base = cols // max_bloques
    extra = cols % max_bloques

    bloques = [base] * max_bloques
    for i in range(extra):
        bloques[i] += 1
    bloques = [b for b in bloques if b > 0]  # eliminar ceros por si hay pocas columnas

    # 🎫 Generar layout dinámico
    for row in range(1, rows + 1):
        seat_row = []
        idx = 0  # índice sobre las letras de columna
        for i, bloque in enumerate(bloques):
            for _ in range(bloque):
                col = column_letters[idx]
                clase = 'first' if row <= 3 else 'economy'
                seat_row.append((f"{col}{row}", clase))
                idx += 1
            if i < len(bloques) - 1:
                seat_row.append(("PASILLO", None))
        seat_matrix.append(seat_row)

    return render(request, 'plane/details.html', {
        'plane': plane,
        'seat_matrix': seat_matrix,
    })


# --------------------------------------------------------------------
# Función para listar usuarios (sin cambios)
def user_list(request):
    users = UserService.get_all()
    return render(request, 'users/list.html', {'users': users})


# --------------------------------------------------------------------
# Función para registrar usuario (sin cambios)
def user_register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Usuario creado correctamente.")
            return redirect('index')
        else:
            messages.error(request, "Por favor corrige los errores del formulario.")
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


# --------------------------------------------------------------------
# Función para login de usuario (sin cambios)
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
                return redirect('index')
            else:
                messages.error(request, "Credenciales inválidas. Intenta nuevamente.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


# --------------------------------------------------------------------
# Función para listar vuelos (sin cambios)
def flight_list(request):
    flights = FlightService.get_all()
    return render(request, 'flights/list.html', {'flights': flights})


# --------------------------------------------------------------------
# Función para administrar vuelos (sin cambios)
def flight_administration(request):
    flights = FlightService.get_all()
    form = CreateFlightForm()
    form_errors = False
    update_errors = False
    update_form_with_errors = None
    update_flight_id = None

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
                form_errors = True

        elif action == "update":
            update_flight_id = request.POST.get("flight_id")
            flight_to_update = get_object_or_404(Flight, id=update_flight_id)
            update_form_with_errors = UpdateFlightForm(request.POST, flight_id=update_flight_id)
            if update_form_with_errors.is_valid():
                cd = update_form_with_errors.cleaned_data
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
                update_errors = True

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
        if update_errors and str(flight.id) == str(update_flight_id):
            uf = update_form_with_errors
        else:
            uf = UpdateFlightForm(initial={
                'origin': flight.origin,
                'destination': flight.destination,
                'departure_date': flight.departure_date,
                'arrival_date': flight.arrival_date,
                'base_price': flight.base_price,
                'status_id': flight.status_id,
                'plane_id': flight.plane_id,
            }, flight_id=flight.id)
        update_form.append((flight, uf))

    return render(request, 'flights/administration.html', {
        'flights': flights,
        'form': form,
        'form_errors': form_errors,
        'update_form': update_form,
        'update_errors': update_errors,
        'update_flight_id': update_flight_id,
    })
