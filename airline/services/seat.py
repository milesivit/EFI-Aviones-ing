from airline.models import Seat
from airline.repositories.seat import SeatRepository


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
