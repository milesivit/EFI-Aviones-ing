from django.urls import path, include

# Se importan todas las vistas que se usarán en las rutas
from airline.views import (
    add_passenger,
    add_status_flight,
    confirm_reservation,
    download_ticket,
    edit_user,
    flight_administration,
    flight_list,
    help_view,
    plane_detail,
    plane_list,
    reservation_by_flight,
    reservation_by_user,
    select_seat,
    upcoming_flight_list,
    user_list,
    user_login,
    user_register,
)

# Lista de URLs de la aplicación
urlpatterns = [
    # Mostrar todas las reservas de un vuelo específico (vista de administrador)
    path(
        route='reservation-administrator/<int:flight_id>/', 
        view=reservation_by_flight, 
        name='reservation_by_flight'
    ),

    # Descargar el ticket asociado a una reserva
    path(
        route='reservation/<int:reservation_id>/download/', 
        view=download_ticket, 
        name='download_ticket'
    ),

    # Mostrar las reservas del usuario actual
    path(
        route='my-reservations/',
        view=reservation_by_user,
        name='reservation_by_user'
    ),

    # Confirmar la reserva de un asiento para un pasajero en un vuelo específico
    path(
        route='flights/<int:flight_id>/passenger/<int:passenger_id>/seat/<int:seat_id>/confirm/',
        view=confirm_reservation,
        name='confirm_reservation'
    ),

    # Agregar un nuevo estado para los vuelos (por ejemplo: activo, cancelado, retrasado)
    path(
        route='flightstatus/',
        view=add_status_flight,
        name='add_status_flight'
    ),

    # Agregar un pasajero a un vuelo
    path(
        route='flights/<int:flight_id>/add-passenger/', 
        view=add_passenger, 
        name='add_passenger'
    ),

    # Página de ayuda de la aplicación
    path(
        route='help/', 
        view=help_view, 
        name='help_view'
    ),

    # Editar un usuario existente (por ID)
    path(
        route='users/edit/<int:user_id>/',
        view=edit_user,
        name='edit_user'
    ),

    # Seleccionar un asiento para un pasajero en un vuelo
    path(
        route='flights/<int:flight_id>/passengers/<int:passenger_id>/select-seat/',
        view=select_seat,
        name='select_seat'
    ),

    # Listar todos los usuarios
    path(
        route='users/',
        view=user_list,
        name='user_list'
    ),

    # Registrar un nuevo usuario
    path(
        route='users/register/', 
        view=user_register, 
        name='user_register'
    ),

    # Login de usuarios
    path(
        route='users/login/', 
        view=user_login, 
        name='user_login'
    ),

    # Listar todos los aviones
    path(
        route='planes/',
        view=plane_list,
        name='plane_list'
    ),

    # Detalle de un avión específico (por ID)
    path(
        route='planes/details/<int:plane_id>',
        view=plane_detail,
        name='plane_detail'
    ),

    # Mostrar únicamente vuelos futuros disponibles
    path(
        route='flights-availables/',
        view=upcoming_flight_list,
        name='upcoming_flight_list',
    ),

    # Listar todos los vuelos
    path(
        route='flights/',
        view=flight_list,
        name='flight_list',
    ),

    # Administración de vuelos (crear, editar, eliminar)
    path(
        route='flights/flight_administration/',
        view=flight_administration,
        name='flight_administration',
    )
]
