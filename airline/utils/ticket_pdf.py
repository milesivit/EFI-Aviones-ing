from reportlab.pdfgen import canvas  # Importa la clase Canvas para generar PDFs
from reportlab.lib.pagesizes import A4  # Importa tamaño de página A4
from django.http import HttpResponse  # Permite enviar respuestas HTTP desde Django


def generate_ticket_pdf(reservation, ticket):
    """
    Genera un PDF de un ticket de vuelo.
    Parámetros:
    - reservation: instancia de Reservation asociada al ticket
    - ticket: instancia de Ticket a imprimir
    """

    # Creamos una respuesta HTTP con tipo de contenido PDF
    response = HttpResponse(content_type="application/pdf")
    # Indicamos que el PDF se descargará con un nombre basado en el código de reserva
    response["Content-Disposition"] = (
        f'attachment; filename="ticket_{reservation.reservation_code}.pdf"'
    )

    # Creamos el objeto canvas de ReportLab para dibujar en el PDF
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4  # Obtenemos ancho y alto de la página

    # Título del ticket en fuente grande y centrado
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(width / 2, height - 100, "Boleto de Vuelo")

    # Información del ticket en fuente normal
    p.setFont("Helvetica", 12)
    p.drawString(
        100, height - 150, f"Código de Reserva: {reservation.reservation_code}"
    )
    p.drawString(100, height - 170, f"Pasajero: {reservation.passenger.name}")
    p.drawString(
        100,
        height - 190,
        f"Vuelo: {reservation.flight.origin} → {reservation.flight.destination}",
    )
    p.drawString(
        100,
        height - 210,
        f"Asiento: {reservation.seat.row}{reservation.seat.column} ({reservation.seat.seat_type})",
    )
    p.drawString(100, height - 230, f"Precio: ${reservation.price}")
    p.drawString(100, height - 250, f"Código de Ticket: {ticket.barcode}")
    p.drawString(
        100,
        height - 270,
        f"Fecha de Emisión: {ticket.issue_date.strftime('%d/%m/%Y %H:%M')}",
    )

    # Finalizamos la página y guardamos el PDF en la respuesta
    p.showPage()
    p.save()

    # Retornamos la respuesta con el PDF listo para descargar
    return response
