from airline.models import (
    User,
    Plane,
    FlightStatus,
    Flight,
    Passenger,
    Seat,
    Reservation,
    Ticket,
)

from api.serializers import (
    UserSerializer,
    PlaneSerializer,
    FlightSerializer,
    FlightStatusSerializer,
    PassengerSerializer,
    SeatSerializer,
    ReservationSerializer,
    TicketSerializer,
)

from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.generics import (
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveAPIView
)
from django.utils import timezone
from api.mixins import AuthAdminView, AuthView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from api.permissions import TokenPermission

"""
Gestión de Vuelos (API)
"""

#Listar todos los vuelos disponibles.
class FlightAvailableListAPIView(AuthView, ListAPIView):
    """
    /api/flightAvailable/ url
    filtra los vuelos disponibles que seal mayor a la fecha de hoy
    """
    permission_classes = [IsAuthenticated]
    serializer_class = FlightSerializer

    def get_queryset(self):
        return Flight.objects.filter(departure_date__gt=timezone.now()).order_by("departure_date")

#Obtener detalle de un vuelo.
class FlightDetailAPIView(AuthView, RetrieveAPIView):
    """
    GET /api/flightDetail/<pk>/
    da el detalle de un vuelo
    accesible para cualquier usuario autenticado
    """
    permission_classes = [IsAuthenticated]
    serializer_class = FlightSerializer
    queryset = Flight.objects.all()

#filtrar vuelos por origen, destino y fecha.
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

 #---------------------------------------------------------------------------------------------

"""
Gestión de Pasajeros (API)
"""

