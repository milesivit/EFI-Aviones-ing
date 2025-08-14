# Importaciones de terceros (librerías instaladas, en este caso Django)
import string
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from airline.models import Reservation, Passenger, Ticket

# Importaciones internas de la aplicación (modelos, servicios y formularios)
from airline.models import Flight, Plane, Seat
from airline.services.user import UserService
from airline.services.plane import PlaneService
from airline.services.flight import FlightService
from airline.services.passenger import PassengerService
from airline.services.reservation import ReservationService
from airline.services.ticket import TicketService
from airline.services.flight_status import FlightStatusService
from airline.forms import CreateFlightForm, UpdateFlightForm, CreatePlaneForm, UpdatePlaneForm, PassengerForm
from home.forms import RegisterForm, LoginForm
from datetime import datetime
import random
import string
from django.shortcuts import get_object_or_404
import random
import string
from datetime import datetime
from django.http import HttpResponse
from airline.utils.ticket_pdf import generate_ticket_pdf
#------------------------------------------------------------------------
#reservas
from django.shortcuts import redirect

def confirm_reservation(request, flight_id, passenger_id, seat_id):
    flight = get_object_or_404(Flight, id=flight_id)
    passenger = get_object_or_404(Passenger, id=passenger_id)
    seat = get_object_or_404(Seat, id=seat_id)

    if request.method == 'POST':
        seat.status = 'taken'
        seat.save()

        reservation_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        price = flight.base_price

        reservation = ReservationService.create(
            status='confirmed',
            reservation_date=datetime.now(),
            price=price,
            reservation_code=reservation_code,
            flight_id=flight.id,
            passenger_id=passenger.id,
            seat_id=seat.id,
            user_id=request.user.id,
        )

        barcode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        issue_date = datetime.now()
        status = 'active'

        ticket = TicketService.create(
            barcode=barcode,
            issue_date=issue_date,
            status=status,
            reservation_id=reservation.id,
        )

        request.session['ticket_id'] = ticket.id

        # Redirigir a la lista de vuelos
        return redirect('upcoming_flight_list')  

    return render(request, 'reservation/confirm_reservation.html', {
        'flight': flight,
        'passenger': passenger,
        'seat': seat,
    })

def reservation_by_user(request):
    # Obtener las reservas del usuario actual
    reservations = ReservationService.get_by_user(user_id=request.user.id)
    
    return render(
        request,
        'reservation/list.html',
        {'reservations': reservations}
    )

def reservation_by_flight(request, flight_id):
    reservations = ReservationService.get_by_flight(flight_id=flight_id)
    return render(request, 'reservation/administrator.html', {'reservations': reservations})
#----------------------------------------------------------------------------------
#ticket
def download_ticket(request, reservation_id):
    try:
        reservation = ReservationService.get_by_id(reservation_id)
        ticket = reservation.ticket
        return generate_ticket_pdf(reservation, ticket)
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")

#-----------------------------------------------------------------------------------
#flight status

def add_status_flight(request):
    if request.method == 'POST':
        status = request.POST.get('status', '').strip()

        if not status:
            messages.error(request, "El campo 'Estado' es obligatorio.")
            return redirect('add_status_flight')  # O volver a la misma página

        try:
            FlightStatusService.create(status=status)
            messages.success(request, f"Estado '{status}' creado correctamente.")
            return redirect('flight_status_list')  # Redirigir a la lista de estados
        except Exception as e:
            messages.error(request, f"No se pudo crear el estado: {str(e)}")
            return redirect('add_status_flight')

    return render(request, 'flight_status/add_status_flight.html')

# --------------------------------------------------------------------
#passengers 
def add_passenger(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)

    if request.method == 'POST':
        form = PassengerForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            name_clean = cd['name'].strip().lower()
            document_clean = cd['document'].strip()

            # Buscar si ya hay un pasajero con ese documento en este vuelo
            existing = Reservation.objects.filter(
                flight_id=flight,
                passenger__document=document_clean
            ).first()

            if existing:
                form.add_error('name', 'Este pasajero ya está registrado en este vuelo.')
            else:
                # Crear el pasajero
                passenger = PassengerService.create(
                    name=cd['name'],
                    document=cd['document'],
                    document_type=cd['document_type'],
                    email=cd['email'],
                    phone=cd['phone'],
                    birth_date=cd['birth_date'],
                )

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

    max_row = plane.rows
    max_column = plane.columns

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
                row_seats.append(None) 
        seat_matrix.append(row_seats)

    if request.method == 'POST':
        seat_id = request.POST.get('seat_id')
        seat = get_object_or_404(Seat, id=seat_id, plane=plane, status='available')

        seat.status = 'Taken'
        seat.save()

        return redirect('confirm_reservation', flight_id=flight.id, passenger_id=passenger_id, seat_id=seat.id)

    return render(request, 'seat/select_seat.html', {
        'flight': flight,
        'passenger_id': passenger_id,
        'seat_matrix': seat_matrix,
    })

#-----------------------------------------------------------------
def create_seats_for_plane(plane):
    seat_types = ['first_class', 'business', 'economico']  # Lista de tipos
    columns = [chr(ord('A') + i) for i in range(plane.columns)]
    seats = []
    for row in range(1, plane.rows + 1):
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
# vuelos
def flight_list(request):
    flights = FlightService.get_all()
    return render(request, 'flights/list.html', {'flights': flights})

# Función para listar solo vuelos futuros
def upcoming_flight_list(request):
    flights = FlightService.get_upcoming_flights() 
    return render(request, 'flights/flight_available.html', {'flights': flights})

# Función para administrar vuelos 
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
