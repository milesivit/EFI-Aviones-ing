from datetime import datetime
from airline.models import Reservation #esta bien el modelo aca ya que El Service solo recibe o devuelve objetos y llama al Repository para hacer el trabajo real.
from airline.repositories.reservation import ReservationRepository


class ReservationService:

    @staticmethod
    def create(
        status: str,
        reservation_date: datetime,
        price: float,
        reservation_code: str,
        flight_id: int,
        passenger_id: int,
        seat_id: int,
        user_id: int,
    ) -> Reservation:
        return ReservationRepository.create(
            status=status,
            reservation_date=reservation_date,
            price=price,
            reservation_code=reservation_code,
            flight_id=flight_id,
            passenger_id=passenger_id,
            seat_id=seat_id,
            user_id=user_id,
        )

    @staticmethod
    def delete(reservation_id: int) -> bool:
        reservation = ReservationRepository.get_by_id(reservation_id=reservation_id)
        if not reservation:
            raise ValueError("La reserva no existe")
        return ReservationRepository.delete(reservation=reservation)

    @staticmethod
    def update(
        reservation_id: int,
        status: str,
        reservation_date: datetime,
        price: float,
        reservation_code: str,
        flight_id: int,
        passenger_id: int,
        seat_id: int,
        user_id: int,
    ) -> Reservation:
        reservation = ReservationRepository.get_by_id(reservation_id=reservation_id)
        if not reservation:
            raise ValueError("La reserva no existe")
        return ReservationRepository.update(
            reservation=reservation,
            status=status,
            reservation_date=reservation_date,
            price=price,
            reservation_code=reservation_code,
            flight_id=flight_id,
            passenger_id=passenger_id,
            seat_id=seat_id,
            user_id=user_id,
        )

    @staticmethod
    def get_all() -> list[Reservation]:
        return ReservationRepository.get_all()

    @staticmethod
    def get_by_id(reservation_id: int) -> Reservation:
        reservation = ReservationRepository.get_by_id(reservation_id=reservation_id)
        if not reservation:
            raise ValueError("La reserva no existe")
        return reservation

    @staticmethod
    def search_by_status(status: str) -> list[Reservation]:
        reservations = ReservationRepository.search_by_status(status=status)
        if not reservations:
            raise ValueError("No se encontraron reservas con ese estado")
        return reservations

    @staticmethod
    def get_by_user(user_id: int) -> list[Reservation]:
        return ReservationRepository.get_by_user(user_id=user_id)

    @staticmethod
    def get_by_flight(flight_id: int) -> list[Reservation]:
        return ReservationRepository.get_by_flight(flight_id=flight_id)
    
    @staticmethod
    def get_by_passenger(passenger_id: int):
        """
        devuelve todas las reservas asociadas a un pasajero usando el repo
        """
        return ReservationRepository.get_by_passenger(passenger_id)
    
    @staticmethod
    def get_passengers_by_flight(flight_id: int):
        flight = ReservationRepository.get_flight_by_id(flight_id)
        if not flight:
            return None  # la view decide 404

        reservations = ReservationRepository.get_confirmed_reservations_by_flight(flight)
        passengers = [res.passenger for res in reservations]
        return passengers
