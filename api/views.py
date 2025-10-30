from airline.models import (
    User,
    Plane,
    Flight,
    Passenger,
    Seat,
    Reservation,
    Ticket,
)

from api.serializers import (
    PlaneSerializer,
    FlightSerializer,
    PassengerSerializer,
    SeatSerializer,
    ReservationSerializer,
    TicketSerializer,
)

from rest_framework import viewsets
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
)

from api.mixins import AuthAdminView, AuthView
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from api.permissions import TokenPermission

from rest_framework import status
from django.utils.crypto import get_random_string
from rest_framework.pagination import LimitOffsetPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.utils import timezone
from rest_framework.response import Response

from airline.services.plane import PlaneService

"""
Gestión de Vuelos (API)
"""

# Listar todos los vuelos disponibles.
class FlightAvailableListAPIView(AuthView, ListAPIView):
    """
    /api/flightAvailable/ url
    filtra los vuelos disponibles que seal mayor a la fecha de hoy
    """

    permission_classes = [IsAuthenticated]
    serializer_class = FlightSerializer

    def get_queryset(self):
        return Flight.objects.filter(departure_date__gt=timezone.now()).order_by(
            "departure_date"
        )


# Obtener detalle de un vuelo.
class FlightDetailAPIView(AuthView, RetrieveAPIView):
    """
    GET /api/flightDetail/<pk>/
    da el detalle de un vuelo
    accesible para cualquier usuario autenticado
    """

    permission_classes = [IsAuthenticated]
    serializer_class = FlightSerializer
    queryset = Flight.objects.all()


# filtrar vuelos por origen, destino y fecha.
class FlightFilterAPIView(AuthView, ListAPIView):
    """
    GET /api/flightFilter/?origin=<ciudad>&destination=<ciudad>&date=<YYYY-MM-DD>
    ejemplo de url= /api/flightFilter/?origin=Tokio&destination=Nagoya
    filtra vuelos por origen, destino y fecha de salida.
    si no se envia filtro, devuelve todos los vuelos
    """

    permission_classes = [IsAuthenticated]
    serializer_class = FlightSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        qs = Flight.objects.all()

        origin = self.request.query_params.get("origin")
        destination = self.request.query_params.get("destination")
        date = self.request.query_params.get("date")

        if origin:
            qs = qs.filter(origin__icontains=origin)
        if destination:
            qs = qs.filter(destination__icontains=destination)
        if date:
            qs = qs.filter(departure_date__date=date)

        return qs


# Crear, editar y eliminar vuelos (solo administradores).
class FlightViewSet(AuthAdminView, viewsets.ModelViewSet):
    """
    CRUD completo de vuelos (solo para admins)
    - GET /api/flight-vs/
    - POST /api/flight-vs/
    - GET /api/flight-vs/{id}/
    - PUT /api/flight-vs/{id}/
    - PATCH /api/flight-vs/{id}/
    - DELETE /api/flight-vs/{id}/
    """

    queryset = Flight.objects.all().order_by("id")
    serializer_class = FlightSerializer


# ---------------------------------------------------------------------------------------------

"""
Gestión de Pasajeros (API)
"""


# Registrar un pasajero. solo para admin papá
class PassengerViewSet(AuthAdminView, viewsets.ModelViewSet):
    """
    CRUD completo de pasajero (solo para admins)
    - GET /api/passenger-vs/
    - POST /api/passenger-vs/
    - GET /api/passenger-vs/{id}/
    - PUT /api/passenger-vs/{id}/
    - PATCH /api/passenger-vs/{id}/
    - DELETE /api/passenger-vs/{id}/
    """

    queryset = Passenger.objects.all().order_by("id")
    serializer_class = PassengerSerializer


# consultar informacion de un pasajero
class PassengerDetailAPIView(AuthView, RetrieveAPIView):
    """
    GET /api/passengerDetail/<pk>/
    da el detalle de un pasajero
    accesible para cualquier usuario autenticado
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PassengerSerializer
    queryset = Passenger.objects.all()


class ReservationByPassengerAPIView(AuthView, ListAPIView):
    """
    GET /api/reservationsByPassenger/<int:passenger_id>/
    devuelve todas las reservas asociadas a un pasajero
    accesible para cualquier usuario autenticado
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ReservationSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        passenger_id = self.kwargs.get("passenger_id")
        # solo reservas del pasajero especificado
        return Reservation.objects.filter(passenger_id=passenger_id).order_by(
            "-reservation_date"
        )


# ---------------------------------------------------------------------------------------------

"""
Sistema de Reservas (API)
"""


# Crear una reserva para un pasajero en un vuelo.
class CreateReservationAPIView(AuthAdminView, viewsets.ViewSet):
    """
    POST /api/createReservation/
    crea una reserva para un pasajero en un vuelo solo para admin,
    NO HACE FALTA QUE PONGAS ALGO EN LOS CAMPOS STATUS, PRICE Y RESERVATION CODE,
    el asiento debe estar disponible
    """

    permission_classes = [IsAuthenticated]  # tiene q estar autenticado
    serializer_class = ReservationSerializer  # llamamos al serializer

    def create(self, request):  # funcion crear
        data = request.data.copy()  # copia la data

        flight_id = data.get("flight")
        passenger_id = data.get("passenger")
        seat_id = data.get("seat")
        user_id = data.get("user")

        # validaciones basicas
        if not (flight_id and passenger_id and seat_id and user_id):
            return Response(
                {"error": "Faltan campos obligatorios."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            flight = Flight.objects.get(pk=flight_id)  # obtiene los id
            passenger = Passenger.objects.get(pk=passenger_id)
            seat = Seat.objects.get(pk=seat_id)
            user = User.objects.get(pk=user_id)
        except (
            Flight.DoesNotExist,
            Passenger.DoesNotExist,
            Seat.DoesNotExist,
            User.DoesNotExist,
        ):
            return Response(  # si no existe algo tira error
                {"error": "Alguno de los objetos referenciados no existe."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # verifica si el asiento está disponible
        if seat.status.lower() != "available":
            return Response(
                {"error": "El asiento no está disponible."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # genera codigo unico de reserva
        reservation_code = get_random_string(10).upper()

        # usa el base_price del vuelo
        price = flight.base_price

        # crear la reserva
        reservation = Reservation.objects.create(
            status="confirmed",
            price=price,
            reservation_code=reservation_code,
            flight=flight,
            passenger=passenger,
            seat=seat,
            user=user,
        )

        # marca asiento como ocupado
        seat.status = "taken"
        seat.save()

        serializer = ReservationSerializer(reservation)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED
        )  # aca respuesta http 201 de creado


# Seleccionar asiento disponible. este es un poco confuso ya que para seeccionar un asiento disponible necesito crear una reserva, cosa que esta hecho anteriormente
# asi que lo que voy a hacer es un get de asientos disponibles en cada avion
class AvailableSeatsListAPIView(AuthView, ListAPIView):
    """
    GET /api/availableSeats/<int:flight_id>/
    devuelve los asientos disponibles de un vuelo indicado
    (segun el avion asociado al vuelo)
    """

    permission_classes = [IsAuthenticated]  # solo para los autenticados
    serializer_class = SeatSerializer  # trae el serializer
    pagination_class = (
        LimitOffsetPagination  # activa la paginacion si hay muchos resultados
    )

    def get_queryset(self):
        flight_id = self.kwargs.get(
            "flight_id"
        )  # es para pasarle a la url flight_id ya q necesita el id

        try:
            flight = Flight.objects.get(pk=flight_id)
        except Flight.DoesNotExist:
            # retornar queryset vacio si no existe el vuelo
            return Seat.objects.none()

        # obtiene el avion del vuelo
        plane = flight.plane

        # devuelve solo los asientos disponibles
        return Seat.objects.filter(
            plane=plane, status__in=["available", "disponible"]
        ).order_by("id")


# cambiar estado de una reserva solo admin
class ChangeReservationStatusAPIView(AuthAdminView, viewsets.ViewSet):
    """
    PATCH /api/changeReservationStatus/<int:reservation_id>/
    hace que un administrador pueda cambiar el estado de una reserva
    ejemplo:
    {
        "status": "denied"
    }
    """

    permission_classes = [IsAdminUser]  # solo admin
    serializer_class = ReservationSerializer  # traigo el serializer

    def partial_update(self, request, reservation_id=None):
        try:
            reservation = Reservation.objects.get(
                pk=reservation_id
            )  # traigo la reserva
        except Reservation.DoesNotExist:  # y sino no existe
            return Response(
                {"error": "La reserva no existe."},
                status=status.HTTP_404_NOT_FOUND,
            )

        new_status = request.data.get("status")  # agarro el estado

        if not new_status:
            return Response(
                {"error": "Debe proporcionar un nuevo estado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # actualiza el estado
        reservation.status = new_status.lower()
        reservation.save()  # lo guarda

        serializer = ReservationSerializer(reservation)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------------------------

"""
Gestión de Aviones y Asientos (API)
"""

#Listar aviones registrados.
class PlaneAPIView(AuthAdminView, APIView):
    """
    lista y administra aviones (solo admins) SIN ID
    """

    serializer_class = PlaneSerializer
    permission_classes = [IsAdminUser]

    def get(self, request):
        planes = PlaneService.get_all()
        serializer = PlaneSerializer(planes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PlaneSerializer(data=request.data)
        if serializer.is_valid():
            plane = serializer.save()
            return Response(PlaneSerializer(plane).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PlaneDetailAPIView(AuthAdminView, APIView):
    """
    obtener, actualizar o eliminar un avión por id
    """

    serializer_class = PlaneSerializer
    permission_classes = [IsAdminUser]

    def get_object(self, pk: int):
        return PlaneService.get_by_id(pk)
    
    def get(self, request, pk: int):
        plane = self.get_object(pk)
        if plane:
            serializer = PlaneSerializer(plane)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "El avión no existe"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk: int):
        plane = self.get_object(pk)
        serializer = PlaneSerializer(plane, data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_plane = serializer.save()
        return Response(PlaneSerializer(updated_plane).data)

    def delete(self, request, pk: int):
        deleted = PlaneService.delete(pk)
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "El avión no existe"}, status=status.HTTP_404_NOT_FOUND)


# obtener layout de asientos de avion
class PlaneLayoutAPIView(AuthView, ListAPIView):
    """
    GET /api/planeLayout/<int:plane_id>/
    Devuelve el layout de los asientos del avion
    Ejemplo de respuesta:
    """

    permission_classes = [IsAuthenticated]  # solo autenticados
    serializer_class = SeatSerializer  # traigo el serializer
    pagination_class = None  # no se pagina devuelve todo el layout

    def list(self, request, plane_id):
        try:
            plane = Plane.objects.get(pk=plane_id)  # traigo el objeto
        except Plane.DoesNotExist:
            return Response(  # sino no existe
                {"error": "El avión no existe."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # trae todos los asientos del avion, ordenados por fila y columna
        seats = Seat.objects.filter(plane=plane).order_by("row", "column")

        # se crea una lista vacia que va a tener una sublista por cada fila del avion
        layout = []
        for r in range(
            1, plane.rows + 1
        ):  # se itera por los numeros de fila desde 1 hasta plane.rows (es decir los que tengaen total)
            row_seats = seats.filter(row=r)
            layout.append(
                [
                    {
                        "number": seat.number,
                        "seat_type": seat.seat_type,
                        "status": seat.status,
                    }
                    for seat in row_seats
                ]
            )

        data = {  # devuelve la estructura JSON al cliente con codigo 200
            "plane": str(plane),
            "rows": plane.rows,
            "columns": plane.columns,
            "layout": layout,
        }

        return Response(data, status=status.HTTP_200_OK)


# verificar disponibilidad de un asiento por codigo
class SeatAvailabilityAPIView(AuthView, RetrieveAPIView):
    """
    GET /api/checkSeatAvailability/<int:plane_id>/<str:seat_code>/
    se verifica si un asiento existe y muestra su estado actual
    solo para usuarios autenticados.
    """

    permission_classes = [IsAuthenticated]  # solo para usuarios autenticados
    serializer_class = SeatSerializer  # se trae el serializer
    queryset = Seat.objects.all()  # traemos todos los objetos de seat

    def get(self, request, seat_code, plane_id):
        try:
            seat = Seat.objects.get(
                plane_id=plane_id, number__iexact=seat_code
            )  # se trae el codigo del asiento
        except Seat.DoesNotExist:
            return Response(  # si no exist eerror
                {"error": "El asiento no existe."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = {  # devuelve la estructura JSON al cliente con codigo 200
            "seat_code": seat.number,
            "plane": str(seat.plane),
            "status": seat.status,
        }

        return Response(data, status=status.HTTP_200_OK)  # la respuesta


# ---------------------------------------------------------------------------------------------
"""
Boletos (API)
"""


# generar boleto a partir de una reserva confirmada
class GenerateTicketAPIView(AuthAdminView, APIView):
    """
    POST /api/generateTicket/<int:reservation_id>/
    crea un boleto (ticket) a partir de una reserva confirmada,
    EL BARCODE SE GENERA SOLO DEJAR CAMPO VACIO
    solo para admin
    """

    permission_classes = [IsAdminUser]  # solo admin
    serializer_class = TicketSerializer  # traigo el serializer

    def post(self, request, reservation_id):
        try:
            reservation = Reservation.objects.get(pk=reservation_id)  # el objeto
        except Reservation.DoesNotExist:
            return Response(  # si no existe error
                {"error": "La reserva no existe."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # ver si la reserva esta confirmada
        if reservation.status.lower() != "confirmed":
            return Response(
                {
                    "error": "Solo se puede generar un boleto a partir de una reserva confirmada."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ver si ya existe un boleto para esta reserva
        if Ticket.objects.filter(reservation=reservation).exists():
            return Response(
                {"error": "Ya existe un boleto para esta reserva."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # crear codigo de barras unico
        barcode = get_random_string(12).upper()

        # crear el boleto
        ticket = Ticket.objects.create(
            barcode=barcode,
            status="active",
            reservation=reservation,
        )

        serializer = TicketSerializer(ticket)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED
        )  # resultado, 201 xq es creacion


# consultar informacion de un boleto por codigo
class TicketInformationAPIView(AuthView, RetrieveAPIView):
    """
    GET /api/ticketInformation/<str:barcode>/
    buscar un ticket por su barcode
    solo para usuarios autenticados
    ej: api/ticketInformation/68N3VEGB4PTD
    """

    permission_classes = [IsAuthenticated]  # solo para usuarios autenticados
    serializer_class = TicketSerializer  # se trae el serializer
    queryset = Ticket.objects.all()  # traemos todos los objetos de seat

    def get(self, request, barcode):
        try:
            ticket = Ticket.objects.get(
                barcode__iexact=barcode
            )  # se trae el codigo del asiento
        except Ticket.DoesNotExist:
            return Response(  # si no exist eerror
                {"error": "El ticket no existe."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = {  # devuelve la estructura JSON al cliente con codigo 200
            "barcode": ticket.barcode,
            "status": ticket.status,
            "reservation": {
                "id": ticket.reservation.id,
                "status": ticket.reservation.status,
                "passenger": str(ticket.reservation.passenger),
                "flight": str(ticket.reservation.flight),
            },
        }

        return Response(data, status=status.HTTP_200_OK)  # la respuesta


# ---------------------------------------------------------------------------------------------

"""
Reportes (API)
"""


# Endpoint para obtener listado de pasajeros por vuelo.
class PassengersByFlightAPIView(AuthView, APIView):
    """
    GET /api/passengersByFlight/<int:flight_id>/
    lista de pasajeros que tienen reservas confirmadas en un vuelo
    solo para usuarios autenticados
    """

    permission_classes = [IsAuthenticated]  # solo autenticados
    serializer_class = PassengerSerializer

    def get(self, request, flight_id):
        try:
            flight = Flight.objects.get(pk=flight_id)  # agarramos el objeto
        except Flight.DoesNotExist:  # si no esta pa casa
            return Response(
                {"error": "El vuelo no existe."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # filtra las reservas confirmadas de ese vuelo
        reservations = Reservation.objects.filter(flight=flight, status="confirmed")

        # obtiene los pasajeros unicos de esas reservas
        passengers = [res.passenger for res in reservations]

        serializer = PassengerSerializer(passengers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)  # respuesta


# Endpoint para obtener reservas activas de un pasajero.
class ActiveReservationsByPassengerAPIView(AuthView, APIView):
    """
    GET /api/activeReservations/<int:passenger_id>/
    devuelve todas las reservas activas (confirmed) de un pasajero
    solo para usuarios autenticados
    """

    permission_classes = [IsAuthenticated]  # solo autenticados
    serializer_class = ReservationSerializer

    def get(self, request, passenger_id):
        try:
            passenger = Passenger.objects.get(pk=passenger_id)  # traigo el obj
        except Passenger.DoesNotExist:
            return Response(  # sino error
                {"error": "El pasajero no existe."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # filtra las reservas activas del pasajero
        active_reservations = Reservation.objects.filter(
            passenger=passenger, status="confirmed"
        )

        serializer = ReservationSerializer(active_reservations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)  # resultado
