from datetime import datetime, timedelta
from airline.models import Flight, Plane, User


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
        status: str,
        base_price: float,
        plane_id: int,
        user_id: list[int],
    ) -> Flight:
        """
        Crea un nuevo vuelo en la base de datos.

        Args:
            origin: Origen del vuelo.
            destination: Destino del vuelo.
            departure_date: Fecha y hora de salida.
            arrival_date: Fecha y hora de llegada.
            duration: Duración del vuelo.
            status: Estado del vuelo.
            base_price: Precio base del vuelo.
            plane_id: ID del avión asignado.
            user_id: Lista de IDs de usuarios asociados al vuelo.

        Returns:
            Instancia del vuelo creado.
        """
        plane = Plane.objects.get(id=plane_id)

        flight = Flight.objects.create(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            arrival_date=arrival_date,
            duration=duration,
            status=status,
            base_price=base_price,
            plane_id=plane,
        )

        users = User.objects.filter(id__in=user_id)
        flight.user_id.set(users)  # Relación ManyToMany
        return flight

    @staticmethod
    def delete(flight: Flight) -> bool:
        """
        Elimina un vuelo de la base de datos.

        Args:
            flight: Instancia del vuelo a eliminar.

        Returns:
            True si la eliminación fue exitosa.

        Raises:
            ValueError: Si el vuelo no existe.
        """
        try:
            flight.delete()
            return True
        except Flight.DoesNotExist:
            raise ValueError("El vuelo no existe")

    @staticmethod
    def update(
        flight: Flight,
        origin: str,
        destination: str,
        departure_date: datetime,
        arrival_date: datetime,
        duration: timedelta,
        status: str,
        base_price: float,
        plane_id: int,
        user_id: list[int],
    ) -> Flight:
        """
        Actualiza los datos de un vuelo existente.

        Args:
            flight: Instancia del vuelo a actualizar.
            origin: Nuevo origen.
            destination: Nuevo destino.
            departure_date: Nueva fecha de salida.
            arrival_date: Nueva fecha de llegada.
            duration: Nueva duración.
            status: Nuevo estado.
            base_price: Nuevo precio base.
            plane_id: Nuevo ID de avión.
            user_id: Nueva lista de IDs de usuarios.

        Returns:
            Vuelo actualizado.
        """
        flight.origin = origin
        flight.destination = destination
        flight.departure_date = departure_date
        flight.arrival_date = arrival_date
        flight.duration = duration
        flight.status = status
        flight.base_price = base_price
        flight.plane_id = Plane.objects.get(id=plane_id)

        users = User.objects.filter(id__in=user_id)
        flight.user_id.set(users)

        flight.save()
        return flight

    @staticmethod
    def get_all() -> list[Flight]:
        """
        Obtiene todos los vuelos registrados.

        Returns:
            Lista de todos los vuelos.
        """
        return Flight.objects.all()

    @staticmethod
    def get_by_id(flight_id: int) -> Flight:
        """
        Obtiene un vuelo por su ID.

        Args:
            flight_id: ID del vuelo.

        Returns:
            Instancia del vuelo o None si no se encuentra.
        """
        try:
            return Flight.objects.get(id=flight_id)
        except Flight.DoesNotExist:
            return None

    @staticmethod
    def search_by_origin(origin: str) -> list[Flight]:
        """
        Busca vuelos cuyo origen contenga una cadena determinada (búsqueda parcial).

        Args:
            origin: Texto a buscar en el origen.

        Returns:
            Lista de vuelos que coinciden con el origen buscado.
        """
        return Flight.objects.filter(origin__icontains=origin)
