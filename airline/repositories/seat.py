from airline.models import Seat, Plane
from typing import Optional


class SeatRepository:
    """
    Repositorio para manipular asientos.
    """

    @staticmethod
    def create(
        number: str,
        row: int,
        column: str,
        seat_type: str,
        status: str,
        plane_id: int,
    ) -> Seat:
        try:
            plane = Plane.objects.get(id=plane_id)
        except Plane.DoesNotExist:
            raise ValueError(f"No se encontró el avión con ID {plane_id}")

        return Seat.objects.create(
            number=number,
            row=row,
            column=column,
            seat_type=seat_type,
            status=status,
            plane=plane,
        )

    @staticmethod
    def delete(seat: Seat) -> bool:
        try:
            seat.delete()
            return True
        except Seat.DoesNotExist:
            raise ValueError("El asiento no existe")

    @staticmethod
    def update(
        seat: Seat,
        number: str,
        row: int,
        column: str,
        seat_type: str,
        status: str,
        plane_id: int
    ) -> Seat:
        try:
            plane = Plane.objects.get(id=plane_id)
        except Plane.DoesNotExist:
            raise ValueError(f"No se encontró el avión con ID {plane_id}")

        seat.number = number
        seat.row = row
        seat.column = column
        seat.seat_type = seat_type
        seat.status = status
        seat.plane = plane
        seat.save()
        return seat

    @staticmethod
    def get_all() -> list[Seat]:
        return Seat.objects.all()

    @staticmethod
    def get_by_id(seat_id: int) -> Optional[Seat]:
        try:
            return Seat.objects.get(id=seat_id)
        except Seat.DoesNotExist:
            return None

    @staticmethod
    def search_by_number(number: str) -> list[Seat]:
        return Seat.objects.filter(number__icontains=number)
