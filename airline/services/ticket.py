from datetime import datetime
from airline.models import (
    Ticket,
)  # esta bien el modelo aca ya que El Service solo recibe o devuelve objetos y llama al Repository para hacer el trabajo real.
from airline.repositories.ticket import TicketRepository
from airline.repositories.reservation import ReservationRepository


class TicketService:
    """
    Servicio que actúa como intermediario entre la lógica de negocio y el repositorio de Ticket.
    """

    @staticmethod
    def create(
        barcode: str,
        issue_date: datetime,
        status: str,
        reservation_id: int,
    ) -> Ticket:
        """
        Crea un nuevo ticket utilizando el repositorio.
        """
        # Obtener instancia de Reservation
        reservation = ReservationRepository.get_by_id(reservation_id=reservation_id)

        return TicketRepository.create(
            barcode=barcode,
            issue_date=issue_date,
            status=status,
            reservation_id=reservation.id,
        )

    @staticmethod
    def delete(ticket_id: int) -> bool:
        """
        Elimina un ticket por su ID, si existe.
        """
        ticket = TicketRepository.get_by_id(ticket_id=ticket_id)
        if ticket:
            return TicketRepository.delete(ticket=ticket)
        return False

    @staticmethod
    def update(
        ticket_id: int,
        barcode: str,
        issue_date: datetime,
        status: str,
        reservation_id: int,
    ) -> bool:
        """
        Actualiza los campos de un ticket existente.
        """
        ticket = TicketRepository.get_by_id(ticket=ticket_id)
        if ticket:
            return TicketRepository.update(
                ticket_id=ticket,
                barcode=barcode,
                issue_date=issue_date,
                status=status,
                reservation_id=reservation_id,
            )
        return False

    @staticmethod
    def get_all() -> list[Ticket]:
        """
        Devuelve una lista con todos los tickets.
        """
        return TicketRepository.get_all()

    @staticmethod
    def get_by_id(ticket_id: int) -> Ticket:
        """
        Devuelve un ticket por su ID. Lanza un error si no existe.
        """
        ticket = TicketRepository.get_by_id(ticket_id=ticket_id)
        if ticket:
            return ticket
        raise ValueError("El Ticket no existe")

    @staticmethod
    def search_by_barcode(barcode: str) -> list[Ticket]:
        """
        Busca tickets por su código de barras. Lanza un error si no se encuentra.
        """
        tickets = TicketRepository.search_by_barcode(barcode=barcode)
        if tickets:
            return tickets
        raise ValueError("No se encontraron tickets con ese código de barras")

    @staticmethod
    def get_ticket_info(barcode: str):
        ticket = TicketRepository.get_ticket_by_barcode(barcode)
        if not ticket:
            return None  # la view decide si lanza 404

        return {
            "barcode": ticket.barcode,
            "status": ticket.status,
            "reservation": {
                "id": ticket.reservation.id,
                "status": ticket.reservation.status,
                "passenger": str(ticket.reservation.passenger),
                "flight": str(ticket.reservation.flight),
            },
        }
