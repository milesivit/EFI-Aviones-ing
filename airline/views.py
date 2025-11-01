# Librerías estándar
from datetime import datetime
import random
import string

# Librerías de terceros (Django)
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

# Modelos internos de la aplicación
from airline.models import (
    Flight,
    Plane,
    Reservation,
    Seat,
)  # TODO ARREGLAR ESTO Q NO LE PEGUE AL MODELO

# Formularios internos
from airline.forms import (
    CreateFlightForm,
    CreatePlaneForm,
    PassengerForm,
    UpdateFlightForm,
    UpdatePlaneForm,
)
from home.forms import LoginForm, RegisterForm

# Servicios internos
from airline.services.flight import FlightService
from airline.services.flight_status import FlightStatusService
from airline.services.passenger import PassengerService
from airline.services.plane import PlaneService
from airline.services.reservation import ReservationService
from airline.services.ticket import TicketService
from airline.services.user import UserService
from airline.services.seat import SeatService

# Utilidades internas
from airline.utils.ticket_pdf import generate_ticket_pdf


# ------------------------------------------------------------------------
# reservas
def confirm_reservation(request, flight_id, passenger_id, seat_id):
    # Obtiene el vuelo, pasajero y asiento correspondientes a los IDs proporcionados.
    # Si no existen, devuelve un error 404.
    try:
        flight = FlightService.get_by_id(flight_id)
        passenger = PassengerService.get_by_id(passenger_id)
        seat = SeatService.get_by_id(seat_id)
    except ValueError as e:
        return render(request, "errors/404.html", {"error": str(e)})

    # Si el método de la petición es POST, significa que se envió el formulario de confirmación
    if request.method == "POST":
        # Cambia el estado del asiento a "taken" (ocupado) y guarda el cambio
        SeatService.mark_as_taken(seat.id)

        # Genera un código de reserva aleatorio de 8 caracteres (letras y números)
        reservation_code = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=8)
        )
        # Obtiene el precio base del vuelo
        price = flight.base_price

        # Crea una nueva reserva usando el servicio de reservas
        reservation = ReservationService.create(
            status="confirmed",  # Estado de la reserva
            reservation_date=datetime.now(),  # Fecha de la reserva
            price=price,  # Precio de la reserva
            reservation_code=reservation_code,  # Código único de la reserva
            flight_id=flight.id,  # ID del vuelo
            passenger_id=passenger.id,  # ID del pasajero
            seat_id=seat.id,  # ID del asiento
            user_id=request.user.id,  # ID del usuario que realiza la reserva
        )

        # Genera un código de barras aleatorio para el ticket
        barcode = "".join(random.choices(string.ascii_uppercase + string.digits, k=12))

        # Crea el ticket usando el servicio de tickets
        ticket = TicketService.create(
            barcode=barcode,
            issue_date=datetime.now(),
            status="active",
            reservation_id=reservation.id,  # Asocia el ticket con la reserva creada
        )

        # Guarda el ID del ticket en la sesión para usarlo más adelante si es necesario
        request.session["ticket_id"] = ticket.id

        # Redirige al usuario a la lista de próximos vuelos
        return redirect("upcoming_flight_list")

    # Si no es POST, simplemente muestra la página de confirmación de reserva
    return render(
        request,
        "reservation/confirm_reservation.html",
        {
            "flight": flight,
            "passenger": passenger,
            "seat": seat,
        },
    )


def reservation_by_user(request):
    # Obtiene todas las reservas asociadas al usuario que ha iniciado sesión.
    # Usa el servicio ReservationService para consultar las reservas por user_id.
    reservations = ReservationService.get_by_user(user_id=request.user.id)

    # Renderiza la plantilla "reservation/list.html" pasando las reservas obtenidas
    return render(request, "reservation/list.html", {"reservations": reservations})


def reservation_by_flight(request, flight_id):
    # Obtiene todas las reservas asociadas a un vuelo específico.
    # Usa el servicio ReservationService para consultar las reservas por flight_id.
    reservations = ReservationService.get_by_flight(flight_id=flight_id)

    # Renderiza la plantilla "reservation/administrator.html" pasando las reservas obtenidas
    return render(
        request, "reservation/administrator.html", {"reservations": reservations}
    )


# ----------------------------------------------------------------------------------
# ticket
def download_ticket(request, reservation_id):
    try:
        # Obtiene la reserva correspondiente al ID proporcionado usando el servicio ReservationService
        reservation = ReservationService.get_by_id(reservation_id)

        # Obtiene el ticket asociado a esa reserva
        ticket = reservation.ticket

        # Genera y devuelve un PDF del ticket usando la función generate_ticket_pdf
        return generate_ticket_pdf(reservation, ticket)

    except Exception as e:
        # Si ocurre cualquier error (reserva no encontrada, ticket inexistente, etc.)
        # devuelve una respuesta HTTP mostrando el mensaje de error
        return HttpResponse(f"Error: {str(e)}")


# -----------------------------------------------------------------------------------
# flight status


def add_status_flight(request):
    if request.method == "POST":
        status = request.POST.get("status", "").strip()

        if not status:
            messages.error(request, "El campo 'Estado' es obligatorio.")
            return redirect("add_status_flight")  # O volver a la misma página

        try:
            FlightStatusService.create(status=status)
            messages.success(request, f"Estado '{status}' creado correctamente.")
            return redirect("flight_status_list")  # Redirigir a la lista de estados
        except Exception as e:
            messages.error(request, f"No se pudo crear el estado: {str(e)}")
            return redirect("add_status_flight")

    return render(request, "flight_status/add_status_flight.html")


# --------------------------------------------------------------------
# passengers
def add_passenger(request, flight_id):
    # Obtiene el vuelo correspondiente al ID proporcionado, o devuelve un 404 si no existe
    flight = get_object_or_404(Flight, id=flight_id)

    if request.method == "POST":
        # Si el formulario fue enviado, crea una instancia de PassengerForm con los datos enviados
        form = PassengerForm(request.POST)

        # Valida los datos del formulario
        if form.is_valid():
            cd = form.cleaned_data  # Datos limpios del formulario
            name_clean = (
                cd["name"].strip().lower()
            )  # Nombre limpio (sin espacios y en minúsculas)
            document_clean = cd["document"].strip()  # Documento limpio (sin espacios)

            # Verifica si ya existe un pasajero con el mismo documento en este vuelo
            existing = Reservation.objects.filter(
                flight_id=flight, passenger__document=document_clean
            ).first()

            if existing:
                # Si ya existe, agrega un error al formulario
                form.add_error(
                    "name", "Este pasajero ya está registrado en este vuelo."
                )
            else:
                # Si no existe, crea un nuevo pasajero usando PassengerService
                passenger = PassengerService.create(
                    name=cd["name"],
                    document=cd["document"],
                    document_type=cd["document_type"],
                    email=cd["email"],
                    phone=cd["phone"],
                    birth_date=cd["birth_date"],
                )

                # Redirige a la página de selección de asiento, pasando los IDs del vuelo y pasajero
                return redirect(
                    "select_seat", flight_id=flight.id, passenger_id=passenger.id
                )
    else:
        # Si no es POST, crea un formulario vacío
        form = PassengerForm()

    # Renderiza la plantilla de agregar pasajero, pasando el formulario y el vuelo
    return render(
        request, "passenger/add_passenger.html", {"form": form, "flight": flight}
    )


# ---------------------------------------------------------------
# seat
def select_seat(request, flight_id, passenger_id):
    # Obtiene el vuelo correspondiente al ID, o lanza 404 si no existe
    flight = get_object_or_404(Flight, id=flight_id)
    # Obtiene el avión asociado al vuelo
    plane = flight.plane

    # Obtiene todos los asientos del avión, ordenados por fila y columna
    seats = Seat.objects.filter(plane=plane).order_by("row", "column")

    # Número máximo de filas y columnas del avión
    max_row = plane.rows
    max_column = plane.columns

    # Genera las etiquetas de columnas, por ejemplo ["A", "B", "C", ...]
    columns = [chr(ord("A") + i) for i in range(max_column)]

    # Crea un diccionario para acceder rápidamente a los asientos por fila y columna
    seat_dict = {(seat.row, seat.column): seat for seat in seats}

    # Construye una matriz de asientos para mostrar en la plantilla
    seat_matrix = []
    for row in range(1, max_row + 1):
        row_seats = []
        for col in columns:
            seat = seat_dict.get((row, col))
            if seat:
                row_seats.append(seat)  # Añade el asiento si existe
            else:
                row_seats.append(None)  # Añade None si no hay asiento en esa posición
        seat_matrix.append(row_seats)

    # Si el formulario fue enviado (POST), significa que el usuario seleccionó un asiento
    if request.method == "POST":
        seat_id = request.POST.get("seat_id")  # Obtiene el ID del asiento seleccionado
        # Verifica que el asiento exista, esté en el avión correcto y esté disponible
        seat = get_object_or_404(Seat, id=seat_id, plane=plane, status="available")

        # Marca el asiento como ocupado
        seat.status = "Taken"
        seat.save()

        # Redirige a la confirmación de la reserva, pasando vuelo, pasajero y asiento
        return redirect(
            "confirm_reservation",
            flight_id=flight.id,
            passenger_id=passenger_id,
            seat_id=seat.id,
        )

    # Si no es POST, muestra la página de selección de asiento con la matriz generada
    return render(
        request,
        "seat/select_seat.html",
        {
            "flight": flight,
            "passenger_id": passenger_id,
            "seat_matrix": seat_matrix,
        },
    )


# -----------------------------------------------------------------
def create_seats_for_plane(plane):
    # Definición de los tipos de asiento posibles (aunque en el código se asigna según la fila)
    seat_types = ["first_class", "business", "economico"]

    # Genera la lista de columnas con letras, por ejemplo ["A", "B", "C", ...] según el número de columnas del avión
    columns = [chr(ord("A") + i) for i in range(plane.columns)]

    # Lista que almacenará todos los objetos Seat que se van a crear
    seats = []

    # Recorre todas las filas del avión
    for row in range(1, plane.rows + 1):
        # Asigna el tipo de asiento según la fila:
        # - filas 1-2: primera clase
        # - filas 3-5: business
        # - filas 6 en adelante: económico
        if row <= 2:
            seat_type = "first_class"
        elif row <= 5:
            seat_type = "business"
        else:
            seat_type = "economico"

        # Para cada columna de la fila, crea un asiento
        for col in columns:
            seats.append(
                Seat(
                    number=f"{row}{col}",  # Número de asiento como "1A", "1B", etc.
                    row=row,
                    column=col,
                    seat_type=seat_type,
                    status="available",  # todos los asientos comienzan como disponibles
                    plane=plane,  # Se asigna al avión correspondiente
                )
            )

    # Crea todos los asientos en la base de datos de forma masiva (bulk_create)
    Seat.objects.bulk_create(seats)


def plane_list(request):
    # Obtiene todos los aviones usando el servicio PlaneService
    airplanes = PlaneService.get_all()

    # Inicializa el formulario para crear un avión nuevo
    form = CreatePlaneForm()
    form_errors = False  # Indica si hubo errores al crear un avión
    update_errors = False  # Indica si hubo errores al actualizar un avión
    update_form_with_errors = (
        None  # Guardará el formulario de actualización con errores
    )
    update_plane_id = None  # ID del avión que se está actualizando

    if request.method == "POST":
        action = request.POST.get("action")  # Determina qué acción se está realizando

        # CREAR AVIÓN
        if action == "create":
            form = CreatePlaneForm(request.POST)  # Carga los datos enviados
            if form.is_valid():
                cd = form.cleaned_data
                # Crea un nuevo avión
                new_plane = Plane(
                    model=cd["model"],
                    capacity=cd["capacity"],
                    rows=cd["rows"],
                    columns=cd["columns"],
                )
                new_plane.save()
                # Crea automáticamente los asientos del avión
                create_seats_for_plane(new_plane)
                return redirect("plane_list")  # Redirige a la lista de aviones
            else:
                form_errors = True  # Si hay errores en el formulario

        # ACTUALIZAR AVIÓN
        elif action == "update":
            update_plane_id = request.POST.get("plane_id")
            plane_to_update = get_object_or_404(Plane, id=update_plane_id)
            update_form_with_errors = UpdatePlaneForm(
                request.POST, plane_id=plane_to_update.id
            )
            if update_form_with_errors.is_valid():
                # Guardar cambios manualmente (es un forms.Form, no ModelForm)
                cd = update_form_with_errors.cleaned_data
                plane_to_update.model = cd["model"]
                plane_to_update.capacity = cd["capacity"]
                plane_to_update.rows = cd["rows"]
                plane_to_update.columns = cd["columns"]
                plane_to_update.save()
                return redirect("plane_list")
            else:
                update_errors = True  # Marca que hubo errores en la actualización

        # ELIMINAR AVIÓN
        elif action == "delete":
            plane_id = request.POST.get("plane_id")
            if plane_id:
                try:
                    PlaneService.delete(plane_id)  # Elimina el avión usando el servicio
                    messages.success(request, "Avión eliminado correctamente.")
                except Exception:
                    messages.error(request, "Error al eliminar el avión.")
            else:
                messages.error(request, "No se indicó el ID del avión.")
            return redirect("plane_list")

    # Prepara los formularios de actualización para cada avión
    update_form = []
    for plane in airplanes:
        if update_errors and str(plane.id) == str(update_plane_id):
            uf = update_form_with_errors  # Si hubo errores, muestra el formulario con errores
        else:
            uf = UpdatePlaneForm(
                initial={
                    "model": plane.model,
                    "capacity": plane.capacity,
                    "rows": plane.rows,
                    "columns": plane.columns,
                },
                plane_id=plane.id,
            )
        update_form.append(
            (plane, uf)
        )  # Guarda la tupla (avión, formulario de actualización)

    # Renderiza la plantilla con:
    # - Lista de aviones
    # - Formulario de creación
    # - Formularios de actualización por cada avión
    # - Indicadores de errores
    return render(
        request,
        "plane/list.html",
        {
            "airplanes": airplanes,
            "form": form,
            "form_errors": form_errors,
            "update_form": update_form,
            "update_errors": update_errors,
            "update_plane_id": update_plane_id,
        },
    )


def plane_detail(request, plane_id):
    # Obtiene el avión correspondiente al ID proporcionado o lanza 404 si no existe
    plane = get_object_or_404(Plane, pk=plane_id)

    # Número de filas y columnas del avión
    rows = plane.rows
    cols = plane.columns

    # Letras de las columnas, por ejemplo ["A", "B", "C", ...] según la cantidad de columnas
    column_letters = string.ascii_uppercase[:cols]

    seat_matrix = []  # Lista que contendrá la matriz de asientos para la plantilla

    # 🧠 Dividir columnas en bloques balanceados (máximo 3 bloques para simular secciones con pasillos)
    max_bloques = 3
    base = cols // max_bloques  # Número de columnas por bloque de forma base
    extra = (
        cols % max_bloques
    )  # Columnas sobrantes que se distribuyen en los primeros bloques

    bloques = [base] * max_bloques  # Inicializa los bloques con la cantidad base
    for i in range(extra):
        bloques[i] += 1  # Distribuye las columnas sobrantes

    bloques = [
        b for b in bloques if b > 0
    ]  # Elimina bloques vacíos si hay pocas columnas

    # 🎫 Generar layout dinámico de asientos por fila y columna
    for row in range(1, rows + 1):
        seat_row = []  # Lista de asientos para esta fila
        idx = 0  # Índice para recorrer las letras de columna

        for i, bloque in enumerate(bloques):
            for _ in range(bloque):
                col = column_letters[idx]
                # Asigna tipo de asiento según la fila: filas 1-3 primera clase, el resto económico
                clase = "first" if row <= 3 else "economy"
                seat_row.append(
                    (f"{col}{row}", clase)
                )  # Tupla: número de asiento y clase
                idx += 1
            # Añade un "PASILLO" entre bloques, excepto al final
            if i < len(bloques) - 1:
                seat_row.append(("PASILLO", None))

        seat_matrix.append(seat_row)  # Añade la fila a la matriz de asientos

    # Renderiza la plantilla de detalle del avión con:
    # - el objeto plane
    # - la matriz de asientos (seat_matrix) con distribución y clases
    return render(
        request,
        "plane/details.html",
        {
            "plane": plane,
            "seat_matrix": seat_matrix,
        },
    )


# ------------------------------------------------------------------
# help


def help_view(request):
    # Renderiza la plantilla "help/help.html" sin pasarle ningún dato adicional
    return render(request, "help/help.html")


# --------------------------------------------------------------------
# Función para listar usuarios (sin cambios)
def user_list(request):
    # Obtiene todos los usuarios usando el servicio UserService
    users = UserService.get_all()

    # Renderiza la plantilla "users/list.html" pasando la lista de usuarios
    return render(request, "users/list.html", {"users": users})


def edit_user(request, user_id):
    # Obtiene el usuario correspondiente al ID proporcionado usando UserService
    user = UserService.get_by_id(user_id)

    if request.method == "POST":
        # Si se envió el formulario, obtiene los datos enviados
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Si no se ingresó contraseña, se deja como None para no modificarla
        if not password:
            password = None

        # Actualiza el usuario usando el servicio UserService
        # Se mantiene el rol actual del usuario
        UserService.update(
            user_id=user_id,
            username=username,
            password=password,
            email=email,
            role=user.role,
        )

        # Refrescar la sesión para mantener la autenticación si el usuario se está editando a sí mismo
        # Se obtiene nuevamente el usuario actualizado
        updated_user = UserService.get_by_id(user_id)
        update_session_auth_hash(
            request, updated_user
        )  # IMPORTANTE para no cerrar sesión

        # Redirige a la página principal
        return redirect("/")

    # Si no es POST, muestra el formulario de edición con los datos actuales del usuario
    return render(request, "users/edit_user.html", {"user": user})


def user_register(request):
    if request.method == "POST":
        # Si se envió el formulario, crea una instancia de RegisterForm con los datos enviados
        form = RegisterForm(request.POST)

        if form.is_valid():
            # Si el formulario es válido, guarda el usuario en la base de datos
            user = form.save()

            # Loguea automáticamente al usuario recién creado
            login(request, user)

            # Muestra un mensaje de éxito
            messages.success(request, "Usuario creado correctamente.")

            # Redirige a la página principal
            return redirect("index")
        else:
            # Si hay errores en el formulario, muestra un mensaje de error
            messages.error(request, "Por favor corrige los errores del formulario.")
    else:
        # Si no es POST, crea un formulario vacío
        form = RegisterForm()

    # Renderiza la plantilla de registro, pasando el formulario (vacío o con errores)
    return render(request, "accounts/register.html", {"form": form})


def user_login(request):
    if request.method == "POST":
        # Si se envió el formulario, crea una instancia de LoginForm con los datos enviados
        form = LoginForm(request.POST)

        if form.is_valid():
            # Si el formulario es válido, obtiene los datos limpios
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            # Intenta autenticar al usuario con las credenciales proporcionadas
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Si las credenciales son correctas, loguea al usuario
                login(request, user)

                # Muestra un mensaje de bienvenida
                messages.success(request, f"Bienvenido/a {user.username}")

                # Redirige a la página principal
                return redirect("index")
            else:
                # Si las credenciales son incorrectas, muestra un mensaje de error
                messages.error(request, "Credenciales inválidas. Intenta nuevamente.")
    else:
        # Si no es POST, crea un formulario vacío
        form = LoginForm()

    # Renderiza la plantilla de login pasando el formulario (vacío o con errores)
    return render(request, "accounts/login.html", {"form": form})


# --------------------------------------------------------------------
# vuelos
def flight_list(request):
    # Obtiene todos los vuelos usando FlightService
    flights = FlightService.get_all()

    # Renderiza la plantilla "flights/list.html" pasando la lista de vuelos
    return render(request, "flights/list.html", {"flights": flights})


# Función para listar solo vuelos futuros
def upcoming_flight_list(request):
    # Obtiene únicamente los vuelos que aún no han ocurrido
    flights = FlightService.get_upcoming_flights()

    # Renderiza la plantilla "flights/flight_available.html" pasando estos vuelos
    return render(request, "flights/flight_available.html", {"flights": flights})


# Función para administrar vuelos
def flight_administration(request):
    # Obtiene todos los vuelos usando FlightService
    flights = FlightService.get_all()

    # Inicializa el formulario para crear un nuevo vuelo
    form = CreateFlightForm()
    form_errors = False  # Indica si hubo errores al crear un vuelo
    update_errors = False  # Indica si hubo errores al actualizar un vuelo
    update_form_with_errors = (
        None  # Guardará el formulario de actualización con errores
    )
    update_flight_id = None  # ID del vuelo que se está actualizando

    if request.method == "POST":
        action = request.POST.get("action")  # Determina qué acción se está realizando

        # CREAR VUELO
        if action == "create":
            form = CreateFlightForm(request.POST)  # Carga los datos enviados
            if form.is_valid():
                cd = form.cleaned_data
                # Crea un nuevo vuelo
                new_flight = Flight(
                    origin=cd["origin"],
                    destination=cd["destination"],
                    departure_date=cd["departure_date"],
                    arrival_date=cd["arrival_date"],
                    duration=cd["arrival_date"] - cd["departure_date"],
                    base_price=cd["base_price"],
                    status=cd["status_id"],
                    plane=cd["plane_id"],
                )
                new_flight.save()
                return redirect("flight_administration")  # Redirige a la misma vista
            else:
                form_errors = True  # Marca que hubo errores al crear

        # ACTUALIZAR VUELO
        elif action == "update":
            update_flight_id = request.POST.get("flight_id")
            flight_to_update = get_object_or_404(Flight, id=update_flight_id)
            update_form_with_errors = UpdateFlightForm(
                request.POST, flight_id=update_flight_id
            )
            if update_form_with_errors.is_valid():
                cd = update_form_with_errors.cleaned_data
                # Actualiza los campos del vuelo
                flight_to_update.origin = cd["origin"]
                flight_to_update.destination = cd["destination"]
                flight_to_update.departure_date = cd["departure_date"]
                flight_to_update.arrival_date = cd["arrival_date"]
                flight_to_update.duration = cd["arrival_date"] - cd["departure_date"]
                flight_to_update.base_price = cd["base_price"]
                flight_to_update.status_id = cd["status_id"]
                flight_to_update.plane_id = cd["plane_id"]
                flight_to_update.save()
                return redirect("flight_administration")
            else:
                update_errors = True  # Marca que hubo errores en la actualización

        # ELIMINAR VUELO
        elif action == "delete":
            flight_id = request.POST.get("flight_id")
            if flight_id:
                try:
                    FlightService.delete(
                        flight_id
                    )  # Elimina el vuelo usando el servicio
                    messages.success(request, "Vuelo eliminado correctamente.")
                except Exception:
                    messages.error(request, "Error al eliminar el vuelo.")
            else:
                messages.error(request, "No se indicó el ID del vuelo.")
            return redirect("flight_administration")

    # Prepara los formularios de actualización para cada vuelo
    update_form = []
    for flight in flights:
        if update_errors and str(flight.id) == str(update_flight_id):
            uf = update_form_with_errors  # Si hubo errores, muestra el formulario con errores
        else:
            uf = UpdateFlightForm(
                initial={
                    "origin": flight.origin,
                    "destination": flight.destination,
                    "departure_date": flight.departure_date,
                    "arrival_date": flight.arrival_date,
                    "base_price": flight.base_price,
                    "status_id": flight.status_id,
                    "plane_id": flight.plane_id,
                },
                flight_id=flight.id,
            )
        update_form.append(
            (flight, uf)
        )  # Guarda la tupla (vuelo, formulario de actualización)

    # Renderiza la plantilla con:
    # - Lista de vuelos
    # - Formulario de creación
    # - Formularios de actualización por cada vuelo
    # - Indicadores de errores
    return render(
        request,
        "flights/administration.html",
        {
            "flights": flights,
            "form": form,
            "form_errors": form_errors,
            "update_form": update_form,
            "update_errors": update_errors,
            "update_flight_id": update_flight_id,
        },
    )
