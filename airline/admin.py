from django.contrib import admin

from airline.models import (
    Flight,
    FlightStatus,
    Passenger,
    Plane,
    Reservation,
    Seat,
    Ticket,
    User,
)


# Registro del modelo Plane en el panel de administración de Django
@admin.register(Plane)
class PlaneAdmin(admin.ModelAdmin):
    # Columnas que se mostrarán en la lista de aviones en el admin
    list_display = (
        "id",
        "model",
        "capacity",
        "rows",
        "columns",
    )
    # Campos que podrán ser buscados mediante la barra de búsqueda
    search_fields = ("model",)


# Registro del modelo User en el panel de administración
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # Columnas visibles en la lista de usuarios
    list_display = ("username", "email", "role")
    # Filtros disponibles en la barra lateral del admin
    list_filter = ("role",)
    # Campos que podrán ser buscados mediante la barra de búsqueda
    search_fields = ("username", "email")


# Registro del modelo FlightStatus en el panel de administración
@admin.register(FlightStatus)
class FlightStatusAdmin(admin.ModelAdmin):
    # Columnas visibles en la lista de estados de vuelo
    list_display = ("id", "status")

# Registro del modelo Flight en el panel de administración de Django
@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    # Columnas que se mostrarán en la lista de vuelos en el admin
    list_display = (
        "id",
        "origin",
        "destination",
        "departure_date",
        "arrival_date",
        "status",
    )
    # Filtros disponibles en la barra lateral del admin
    list_filter = ("status", "departure_date")
    # Campos que podrán ser buscados mediante la barra de búsqueda
    search_fields = ("origin", "destination")


# Registro del modelo Passenger en el panel de administración
@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    # Columnas visibles en la lista de pasajeros
    list_display = (
        "id",
        "name",
        "document",
        "document_type",
        "email",
        "phone",
        "birth_date",
    )
    # Campos que podrán ser buscados mediante la barra de búsqueda
    search_fields = ("name", "document", "email")

# Registro del modelo Seat en el panel de administración de Django
@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    # Columnas que se mostrarán en la lista de asientos en el admin
    list_display = ("id", "number", "row", "column", "seat_type", "status", "plane_id")
    # Filtros disponibles en la barra lateral del admin
    list_filter = ("seat_type", "status", "plane_id")
    # Campos que podrán ser buscados mediante la barra de búsqueda
    search_fields = ("number",)


# Registro del modelo Reservation en el panel de administración de Django
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    # Columnas visibles en la lista de reservas
    list_display = (
        "id",
        "reservation_code",
        "flight",
        "passenger",
        "seat",
        "status",
        "reservation_date",
        "price",
        "user",
    )
    # Filtros disponibles en la barra lateral del admin
    list_filter = ("status", "reservation_date", "user")
    # Campos que podrán ser buscados mediante la barra de búsqueda
    search_fields = (
        "reservation_code",
        "passenger__name",      # Búsqueda por nombre del pasajero relacionado
        "flight__origin",       # Búsqueda por origen del vuelo relacionado
        "flight__destination",  # Búsqueda por destino del vuelo relacionado
        "user__username",       # Búsqueda por nombre de usuario del creador de la reserva
    )

# Registro del modelo Ticket en el panel de administración de Django
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    # Columnas que se mostrarán en la lista de tickets en el admin
    list_display = ("id", "barcode", "reservation", "issue_date", "status")
    # Filtros disponibles en la barra lateral del admin
    list_filter = ("status", "issue_date")
    # Campos que podrán ser buscados mediante la barra de búsqueda
    search_fields = (
        "barcode",                        # Búsqueda por código de barras del ticket
        "reservation__reservation_code",  # Búsqueda por código de reserva relacionado
    )
