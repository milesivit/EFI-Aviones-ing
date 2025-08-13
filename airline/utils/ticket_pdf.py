from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.http import HttpResponse

def generate_ticket_pdf(reservation, ticket):
    """
    Genera un PDF de un ticket papaaaaaaaaaa
    """
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{reservation.reservation_code}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(width / 2, height - 100, "Boleto de Vuelo")

    p.setFont("Helvetica", 12)
    p.drawString(100, height - 150, f"Código de Reserva: {reservation.reservation_code}")
    p.drawString(100, height - 170, f"Pasajero: {reservation.passenger.name}")
    p.drawString(100, height - 190, f"Vuelo: {reservation.flight.origin} → {reservation.flight.destination}")
    p.drawString(100, height - 210, f"Asiento: {reservation.seat.row}{reservation.seat.column} ({reservation.seat.seat_type})")
    p.drawString(100, height - 230, f"Precio: ${reservation.price}")
    p.drawString(100, height - 250, f"Código de Ticket: {ticket.barcode}")
    p.drawString(100, height - 270, f"Fecha de Emisión: {ticket.issue_date.strftime('%d/%m/%Y %H:%M')}")

    p.showPage()
    p.save()

    return response
