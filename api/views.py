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
from rest_framework.response import Response

from airline.services.plane import PlaneService
from airline.services.flight import FlightService
from airline.services.passenger import PassengerService
from airline.services.reservation import ReservationService
from airline.services.seat import SeatService
from airline.services.ticket import TicketService

"""
Gestión de Vuelos (API)
"""

# Listar todos los vuelos disponibles.
class FlightAvailableListAPIView(AuthView, ListAPIView):
    """
    GET /api/flightAvailable/
    filtra los vuelos disponibles que seal mayor a la fecha de hoy
    """

    permission_classes = [IsAuthenticated]
    serializer_class = FlightSerializer

    def get_queryset(self):
        return FlightService.get_upcoming_flights()
    

# Obtener detalle de un vuelo.
class FlightDetailAPIView(AuthView, RetrieveAPIView):
    """
    GET /api/flightDetail/<pk>/
    da el detalle de un vuelo
    accesible para cualquier usuario autenticado
    """

    permission_classes = [IsAuthenticated]
    serializer_class = FlightSerializer

    def get_object(self):
        flight_id = self.kwargs.get("pk")
        try:
            return FlightService.get_by_id(flight_id)
        except Flight.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound(detail="Flight not found")


# filtrar vuelos por origen, destino y fecha.
class FlightFilterAPIView(AuthView, ListAPIView): #TODO se ve mal en swagger
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
        origin = self.request.query_params.get("origin")
        destination = self.request.query_params.get("destination")
        date = self.request.query_params.get("date")

        return FlightService.filter_flights(origin, destination, date)


#crear, editar y eliminar vuelos (solo administradores).
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

#registrar un pasajero. solo para admin papá
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
    Accesible para cualquier usuario autenticado
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PassengerSerializer

    def get_object(self):
        passenger_id = self.kwargs.get("pk")
        return PassengerService.get_by_id(passenger_id)

#listas reservas asociadas a un pasajero
class ReservationByPassengerAPIView(AuthView, ListAPIView):
    """
    GET /api/reservationsByPassenger/<int:passenger_id>/
    Devuelve todas las reservas asociadas a un pasajero.
    Accesible para cualquier usuario autenticado.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ReservationSerializer
    pagination_class = None

    def get_queryset(self):
        passenger_id = self.kwargs.get("passenger_id")
        return ReservationService.get_by_passenger(passenger_id)


# ---------------------------------------------------------------------------------------------

"""
Sistema de Reservas (API)
"""


# Crear una reserva para un pasajero en un vuelo.
class CreateReservationAPIView(AuthAdminView, viewsets.ViewSet): #TODO NO ANDA NADA 
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
    Devuelve los asientos disponibles de un vuelo indicado
    según el avión asociado al vuelo.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = SeatSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        flight_id = self.kwargs.get("flight_id")
        return SeatService.get_available_seats_by_flight(flight_id)


# cambiar estado de una reserva solo admin
class ChangeReservationStatusAPIView(AuthAdminView, APIView): #TODO NO ANDA EL PATCH
    """
    PATCH /api/changeReservationStatus/<int:reservation_id>/
    Permite que un administrador cambie el estado de una reserva.
    """

    permission_classes = [IsAdminUser]

    def get(self, request, reservation_id=None):
        """
        GET opcional solo para Swagger / testing.
        Devuelve los datos de la reserva.
        """
        try:
            reservation = ReservationService.get_by_id(reservation_id)
        except ValueError:
            return Response(
                {"error": "La reserva no existe."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ReservationSerializer(reservation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, reservation_id=None):
        try:
            reservation = ReservationService.get_by_id(reservation_id)
        except ValueError:
            return Response(
                {"error": "La reserva no existe."},
                status=status.HTTP_404_NOT_FOUND,
            )

        new_status = request.data.get("status")
        if not new_status:
            return Response(
                {"error": "Debe proporcionar un nuevo estado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Cambiamos el estado usando el service
        updated_reservation = ReservationService.update(
            reservation_id=reservation.id,
            status=new_status.lower(),
            reservation_date=reservation.reservation_date,
            price=reservation.price,
            reservation_code=reservation.reservation_code,
            flight_id=reservation.flight.id,
            passenger_id=reservation.passenger.id,
            seat_id=reservation.seat.id,
            user_id=reservation.user.id,
        )

        serializer = ReservationSerializer(updated_reservation)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------------------------

"""
Gestión de Aviones y Asientos (API)
"""

#Listar aviones registrados.
class PlaneViewSet(AuthAdminView, viewsets.ModelViewSet):
    """
    CRUD completo de vuelos (solo para admins)
    - GET /api/plane-vs/
    - POST /api/plane-vs/
    - GET /api/plane-vs/{id}/
    - PUT /api/plane-vs/{id}/
    - PATCH /api/plane-vs/{id}/
    - DELETE /api/plane-vs/{id}/
    """

    queryset = Plane.objects.all().order_by("id")
    serializer_class = PlaneSerializer


# obtener layout de asientos de avion
class PlaneLayoutAPIView(AuthView, ListAPIView):
    """
    GET /api/planeLayout/<int:plane_id>/
    Devuelve el layout de los asientos del avion
    """

    permission_classes = [IsAuthenticated]
    serializer_class = SeatSerializer
    pagination_class = None

    def list(self, request, plane_id):
        data = PlaneService.get_plane_layout(plane_id)
        if not data:
            return Response({"error": "El avión no existe."}, status=status.HTTP_404_NOT_FOUND)
        return Response(data, status=status.HTTP_200_OK)


# verificar disponibilidad de un asiento por codigo
class SeatAvailabilityAPIView(AuthView, RetrieveAPIView):
    """
    GET /api/checkSeatAvailability/<int:plane_id>/<str:seat_code>/
    Verifica si un asiento existe y muestra su estado actual
    api/checkSeatAvailability/4/1A/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, plane_id, seat_code):
        data = SeatService.check_availability(plane_id, seat_code)
        if not data:
            return Response({"error": "El asiento no existe."}, status=status.HTTP_404_NOT_FOUND)
        return Response(data, status=status.HTTP_200_OK)


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
    Buscar un ticket por su barcode
    por ejemplo /api/ticketInformation/Y8C5TLQEGZ39
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, barcode):
        data = TicketService.get_ticket_info(barcode)
        if not data:
            return Response({"error": "El ticket no existe."}, status=status.HTTP_404_NOT_FOUND)
        return Response(data, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------------------------

"""
Reportes (API)
"""


# Endpoint para obtener listado de pasajeros por vuelo.
class PassengersByFlightAPIView(AuthView, APIView):
    """
    GET /api/passengersByFlight/<int:flight_id>/
    Lista de pasajeros con reservas confirmadas en un vuelo
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, flight_id):
        passengers = ReservationService.get_passengers_by_flight(flight_id)
        if passengers is None:
            return Response({"error": "El vuelo no existe."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PassengerSerializer(passengers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Endpoint para obtener reservas activas de un pasajero.
class ActiveReservationsByPassengerAPIView(AuthView, APIView):
    """
    GET /api/activeReservations/<int:passenger_id>/
    Devuelve todas las reservas activas (confirmed) de un pasajero
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, passenger_id):
        active_reservations = PassengerService.get_active_reservations(passenger_id)
        if active_reservations is None:
            return Response({"error": "El pasajero no existe."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReservationSerializer(active_reservations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
