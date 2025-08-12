# Importaciones de terceros (librerías instaladas, en este caso Django)
import string
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth import authenticate, login
from airline.models import Reservation, Passenger

# Importaciones internas de la aplicación (modelos, servicios y formularios)
from airline.models import Flight, Plane, Seat
from airline.services.user import UserService
from airline.services.plane import PlaneService
from airline.services.flight import FlightService
from airline.services.passenger import PassengerService
from airline.forms import CreateFlightForm, UpdateFlightForm, CreatePlaneForm, UpdatePlaneForm, PassengerForm
from home.forms import RegisterForm, LoginForm

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import FlightStatus
import json

@csrf_exempt
def flight_status_list(request):
    if request.method == 'GET':
        statuses = list(FlightStatus.objects.values())
        return JsonResponse(statuses, safe=False)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        status = data.get('status')
        new_status = FlightStatus.objects.create(status=status)
        return JsonResponse({"id": new_status.id, "status": new_status.status})
# --------------------------------------------------------------------
#passengers 

def add_passenger(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)

    if request.method == 'POST':
        form = PassengerForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            # Crear pasajero usando el servicio
            passenger = PassengerService.create(
                name=cd['name'],
                document=cd['document'],
                document_type=cd['document_type'],
                email=cd['email'],
                phone=cd['phone'],
                birth_date=cd['birth_date'],
            )

            # Aquí podés crear la reserva, asignar asiento, etc.

            # Por ahora, redirijo a lista vuelos, podés cambiar a donde quieras
            return redirect('select_seat', flight_id=flight.id, passenger_id=passenger.id)

    else:
        form = PassengerForm()
    
    return render(request, 'passenger/add_passenger.html', {'form': form, 'flight': flight})

#---------------------------------------------------------------
#seat
def select_seat(request, flight_id, passenger_id):
    flight = get_object_or_404(Flight, id=flight_id)
    plane = flight.plane

    seats = Seat.objects.filter(plane=plane).order_by('row', 'column')

    # Crear matriz de asientos por fila y columna, con "PASILLO" en el medio (ejemplo)
    max_row = plane.rows
    max_column = plane.columns

    # Supongo que las columnas son letras 'A', 'B', 'C', ...
    columns = [chr(ord('A') + i) for i in range(max_column)]

    seat_dict = {(seat.row, seat.column): seat for seat in seats}

    seat_matrix = []
    for row in range(1, max_row + 1):
        row_seats = []
        for col in columns:
            seat = seat_dict.get((row, col))
            if seat:
                row_seats.append(seat)
            else:
                row_seats.append(None)  # espacio vacío o pasillo
        seat_matrix.append(row_seats)

    if request.method == 'POST':
        seat_id = request.POST.get('seat_id')
        seat = get_object_or_404(Seat, id=seat_id, plane=plane, status='available')

        # Crear reserva o actualizarla (tu lógica)
        # Reservation.objects.create(flight=flight, passenger_id=passenger_id, seat=seat)

        seat.status = 'Taken'
        seat.save()

        return redirect('flight_list')

    return render(request, 'seat/select_seat.html', {
        'flight': flight,
        'passenger_id': passenger_id,
        'seat_matrix': seat_matrix,
    })

#-----------------------------------------------------------------
# Función para listar aviones y manejar creación, actualización y eliminación
def create_seats_for_plane(plane):
    seat_types = ['first_class', 'business', 'economico']  # Lista de tipos
    columns = [chr(ord('A') + i) for i in range(plane.columns)]
    seats = []
    for row in range(1, plane.rows + 1):
        # Elegir tipo según fila, o cualquier otra regla
        if row <= 2:
            seat_type = 'first_class'
        elif row <= 5:
            seat_type = 'business'
        else:
            seat_type = 'economico'
        
        for col in columns:
            seats.append(Seat(
                number=f"{row}{col}",
                row=row,
                column=col,
                seat_type=seat_type,
                status='available',
                plane=plane
            ))
    Seat.objects.bulk_create(seats)

    
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
                create_seats_for_plane(new_plane)
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

#------------------------------------------------------------------
#help

def help_view(request):
    return render(request, 'help/help.html')

# --------------------------------------------------------------------
# Función para listar usuarios (sin cambios)
def user_list(request):
    users = UserService.get_all()
    return render(request, 'users/list.html', {'users': users})

from django.contrib.auth import update_session_auth_hash

def edit_user(request, user_id):
    user = UserService.get_by_id(user_id)

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not password:
            password = None  

        UserService.update(
            user_id=user_id,
            username=username,
            password=password,
            email=email,
            role=user.role,
        )
        
        # Refrescar sesión para mantener autenticación
        # Volvemos a obtener el usuario actualizado:
        updated_user = UserService.get_by_id(user_id)
        update_session_auth_hash(request, updated_user)  # IMPORTANTE

        return redirect('/')

    return render(request, 'users/edit_user.html', {'user': user})



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
