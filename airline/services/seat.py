from airline.models import Seat, Flight #esta bien el modelo aca ya que El Service solo recibe o devuelve objetos y llama al Repository para hacer el trabajo real.
from airline.repositories.seat import SeatRepository
from airline.repositories.flight import FlightRepository
from typing import List

class SeatService:

    @staticmethod
    def create(
        number: str,
        row: int,
        column: str,
        seat_type: str,
        status: str,
        plane_id: int,
    ) -> Seat:
        return SeatRepository.create(
            number=number,
            row=row,
            column=column,
            seat_type=seat_type,
            status=status,
            plane_id=plane_id,
        )

    @staticmethod
    def delete(seat_id: int) -> bool:
        seat = SeatRepository.get_by_id(seat_id=seat_id)
        if seat:
            return SeatRepository.delete(seat=seat)
        return False

    @staticmethod
    def update(
        seat_id: int,
        number: str,
        row: int,
        column: str,
        seat_type: str,
        status: str,
        plane_id: int,
    ) -> bool:
        seat = SeatRepository.get_by_id(seat_id=seat_id)
        if seat:
            SeatRepository.update(
                seat=seat,
                number=number,
                row=row,
                column=column,
                seat_type=seat_type,
                status=status,
                plane_id=plane_id,
            )

    @staticmethod
    def get_all() -> list[Seat]:
        return SeatRepository.get_all()

    @staticmethod
    def get_by_id(seat_id: int) -> list[Seat]:
        if seat_id:
            return SeatRepository.get_by_id(seat_id=seat_id)
        return ValueError("El Asiento No Existe")

    @staticmethod
    def search_by_number(number: str) -> list[Seat]:
        if number:
            return SeatRepository.search_by_number(number=number)
        return ValueError("El Asiento No Existe")
    
    @staticmethod
    def mark_as_taken(seat_id: int) -> Seat:
        return SeatRepository.mark_as_taken(seat_id)
    
    @staticmethod
    def get_available_seats_by_flight(flight_id: int) -> List[Seat]:
        flight = FlightRepository.get_by_id(flight_id)
        if not flight:
            return []

        plane_id = flight.plane.id
        return SeatRepository.get_available_by_plane(plane_id)
    
    @staticmethod
    def check_availability(plane_id: int, seat_code: str):
        seat = SeatRepository.get_seat_by_plane_and_code(plane_id, seat_code)
        if not seat:
            return None  # la view se encarga del 404

        return {
            "seat_code": seat.number,
            "plane": str(seat.plane),
            "status": seat.status,
        }