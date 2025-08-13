from django.contrib import admin
from airline.models import Plane, User, Flight, FlightStatus, Passenger, Seat, Reservation, Ticket

@admin.register(Plane)
class PlaneAdmin(admin.ModelAdmin):
    list_display = ('id', 'model', 'capacity', 'rows', 'columns') #columnas visibles en el listado
    search_fields = ('model',)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role')
    list_filter = ('role',)
    search_fields = ('username', 'email') #barra de busqueda

@admin.register(FlightStatus)
class FlightStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'status')

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('id', 'origin', 'destination', 'departure_date', 'arrival_date', 'status')
    list_filter = ('status', 'departure_date') #filtros laterales
    search_fields = ('origin', 'destination')

@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'document', 'document_type', 'email', 'phone', 'birth_date')
    search_fields = ('name', 'document', 'email')

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('id', 'number', 'row', 'column', 'seat_type', 'status', 'plane_id')
    list_filter = ('seat_type', 'status', 'plane_id')
    search_fields = ('number',)

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'reservation_code', 'flight', 'passenger', 'seat', 'status', 'reservation_date', 'price', 'user')
    list_filter = ('status', 'reservation_date', 'user')
    search_fields = ('reservation_code', 'passenger__name', 'flight__origin', 'flight__destination', 'user__username')

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'barcode', 'reservation', 'issue_date', 'status')
    list_filter = ('status', 'issue_date')
    search_fields = ('barcode', 'reservation__reservation_code')
