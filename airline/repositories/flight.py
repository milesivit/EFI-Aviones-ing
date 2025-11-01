from datetime import datetime, timedelta
from airline.models import Flight, FlightStatus, Plane, User


class FlightRepository:
    """
    Repositorio para manipular objetos Flight (vuelos) en la base de datos.
    """

    @staticmethod
    def create(
        origin: str,
        destination: str,
        departure_date: datetime,
        arrival_date: datetime,
        duration: timedelta,
        status: int,  # ahora recibe ID
        base_price: float,
        plane_id: int,
        user_id: list[int],
    ) -> Flight:
        """
        Crea un nuevo vuelo en la base de datos.
        """
        flight = Flight.objects.create(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            arrival_date=arrival_date,
            duration=duration,
            base_price=base_price,
            status_id=status,  # ⚠️ usar _id
            plane_id=plane_id,  # ⚠️ usar ID directamente
        )

        # Relación ManyToMany
        users = User.objects.filter(id__in=user_id)
        flight.user.set(users)

        return flight

    @staticmethod
    def update(
        flight: Flight,
        origin: str,
        destination: str,
        departure_date: datetime,
        arrival_date: datetime,
        duration: timedelta,
        status: int,  # recibe ID
        base_price: float,
        plane_id: int,
        user_id: list[int],
    ) -> Flight:
        """
        Actualiza los datos de un vuelo existente.
        """
        flight.origin = origin
        flight.destination = destination
        flight.departure_date = departure_date
        flight.arrival_date = arrival_date
        flight.duration = duration
        flight.base_price = base_price
        flight.status_id = status  # ⚠️ usar _id
        flight.plane_id = plane_id  # ⚠️ pasar solo ID

        # Actualizar ManyToMany
        users = User.objects.filter(id__in=user_id)
        flight.user.set(users)

        flight.save()
        return flight

    @staticmethod
    def delete(flight: Flight) -> bool:
        try:
            flight.delete()
            return True
        except Flight.DoesNotExist:
            raise ValueError("El vuelo no existe")

    @staticmethod
    def get_all() -> list[Flight]:
        return Flight.objects.all()

    @staticmethod
    def get_by_id(flight_id: int) -> Flight:
        try:
            return Flight.objects.get(id=flight_id)
        except Flight.DoesNotExist:
            return None

    @staticmethod
    def search_by_origin(origin: str) -> list[Flight]:
        return Flight.objects.filter(origin__icontains=origin)

    @staticmethod
    def filter_flights(origin=None, destination=None, date=None):
        qs = Flight.objects.all()
        if origin:
            qs = qs.filter(origin__icontains=origin)
        if destination:
            qs = qs.filter(destination__icontains=destination)
        if date:
            qs = qs.filter(departure_date__date=date)
        return qs
