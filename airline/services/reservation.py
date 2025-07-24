from datetime import datetime
from airline.models import Reservation
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
    ) -> Reservation:
        return ReservationRepository.create(
            status=status,
            reservation_date=reservation_date,
            price=price,
            reservation_code=reservation_code,
            flight_id=flight_id,
            passenger_id=passenger_id,
            seat_id=seat_id,
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
