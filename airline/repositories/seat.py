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
        plane_id: int,
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
    
    @staticmethod
    def mark_as_taken(seat_id: int) -> Seat:
        seat = SeatRepository.get_by_id(seat_id)
        if not seat:
            raise ValueError("El asiento no existe.")

        if seat.status == "taken":
            raise ValueError("El asiento ya está ocupado.")

        seat.status = "taken"
        seat.save()
        return seat
    
    @staticmethod
    def verify_seat(seat_id: int, plane: int, status: str) -> list[Seat]:
        seat = SeatRepository.get_by_id(seat_id=seat_id)
        return Seat.objects.filter(seat_id=seat, plane=plane, status="available")
    
    @staticmethod
    def bulk_create(seats) -> list[Seat]:
        """
        Crea múltiples asientos en la base de datos de manera eficiente.
        """
        Seat.objects.bulk_create(seats)