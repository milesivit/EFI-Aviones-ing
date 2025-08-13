from datetime import datetime
from airline.models import Reservation


class ReservationRepository:
    """
    Clase de repositorio que se encargará de conectarse con la base de datos
    para manipular reservas.
    """

    @staticmethod
    def create(
        status: str,
        reservation_date: datetime,
        price: float,
        reservation_code: str,
        flight_id: int,
        passenger_id: int,
        seat_id: int,
        user_id=int,
    ) -> Reservation:
        """
        Crea una nueva reserva.

        Args:
            status: Estado de la reserva.
            reservation_date: Fecha de la reserva.
            price: Precio total de la reserva.
            reservation_code: Código único de reserva.
            flight_id: ID del vuelo asociado.
            passenger_id: ID del pasajero asociado.
            seat_id: ID del asiento reservado.

        Returns:
            Instancia de la reserva creada.
        """
        return Reservation.objects.create(
            status=status,
            reservation_date=reservation_date,
            price=price,
            reservation_code=reservation_code,
            flight_id=flight_id,
            passenger_id=passenger_id,
            seat_id=seat_id,
            user_id=user_id
        )

    @staticmethod
    def delete(reservation: Reservation) -> bool:
        """
        Elimina una reserva de la base de datos.

        Args:
            reservation: Instancia de la reserva a eliminar.

        Returns:
            True si la eliminación fue exitosa.

        Raises:
            ValueError: Si la reserva no existe.
        """
        try:
            reservation.delete()
            return True
        except Reservation.DoesNotExist:
            raise ValueError("La reserva no existe")

    @staticmethod
    def update(
        reservation: Reservation,
        status: str,
        reservation_date: datetime,
        price: float,
        reservation_code: str,
        flight_id: int,
        passenger_id: int,
        seat_id: int,
        user_id: int,
    ) -> Reservation:
        reservation.status = status
        reservation.reservation_date = reservation_date
        reservation.price = price
        reservation.reservation_code = reservation_code
        reservation.flight_id = flight_id
        reservation.passenger_id = passenger_id
        reservation.seat_id = seat_id
        reservation.user_id = user_id
        reservation.save()
        return reservation

    @staticmethod
    def get_all() -> list[Reservation]:
        """
        Obtiene todas las reservas registradas.

        Returns:
            Lista de reservas.
        """
        return Reservation.objects.all()

    @staticmethod
    def get_by_id(reservation_id: int) -> Reservation:
        """
        Obtiene una reserva por su ID.

        Args:
            Reservation_id: ID de la reserva.

        Returns:
            Instancia de la reserva o None si no existe.
        """
        try:
            return Reservation.objects.get(id=reservation_id)
        except Reservation.DoesNotExist:
            return None

    @staticmethod
    def search_by_reservation_code(reservation_code: str) -> list[Reservation]:
        """
        Busca reservas cuyo código contenga el texto dado.

        Args:
            reservation_code: Texto parcial o completo del código.

        Returns:
            Lista de reservas coincidentes.
        """
        return Reservation.objects.filter(reservation_code__icontains=reservation_code)
    
    @staticmethod
    def get_by_user(user_id: int) -> list[Reservation]:
        """
        Obtiene todas las reservas de un usuario específico.
        """
        return Reservation.objects.filter(user_id=user_id)
    
    @staticmethod
    def get_by_flight(flight_id: int) -> list[Reservation]:
        return Reservation.objects.filter(flight_id=flight_id)

    
