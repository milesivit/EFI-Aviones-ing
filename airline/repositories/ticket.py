from datetime import datetime
from typing import Optional
from airline.models import Ticket, Reservation


class TicketRepository:
    """
    Repositorio para manipular boletos.
    """

    @staticmethod
    def create(
        barcode: str,
        issue_date: datetime,
        status: str,
        reservation_id: int,
    ) -> Ticket:
        reservation = Reservation.objects.get(id=reservation_id)
        return Ticket.objects.create(
            barcode=barcode,
            issue_date=issue_date,
            status=status,
            reservation=reservation,
        )

    @staticmethod
    def delete(ticket: Ticket) -> bool:
        try:
            ticket.delete()
            return True
        except Ticket.DoesNotExist:
            raise ValueError("El boleto no existe")

    @staticmethod
    def update(
        ticket: Ticket,
        barcode: str,
        issue_date: datetime,
        status: str,
        reservation_id: int,
    ) -> Ticket:
        reservation = Reservation.objects.get(id=reservation_id)
        ticket.barcode = barcode
        ticket.issue_date = issue_date
        ticket.status = status
        ticket.reservation = reservation
        ticket.save()
        return ticket

    @staticmethod
    def get_all() -> list[Ticket]:
        return Ticket.objects.all()

    @staticmethod
    def get_by_id(ticket_id: int) -> Optional[Ticket]:
        try:
            return Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            return None

    @staticmethod
    def search_by_barcode(barcode: str) -> list[Ticket]:
        return Ticket.objects.filter(barcode__icontains=barcode)

    @staticmethod
    def get_ticket_by_barcode(barcode: str) -> Ticket | None:
        try:
            return Ticket.objects.get(barcode__iexact=barcode)
        except Ticket.DoesNotExist:
            return None
