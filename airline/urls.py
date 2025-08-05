from django.urls import path

from airline.views import (
    user_list,
    plane_list,
    plane_detail,
    user_register,
    user_login,
    flight_list,
    flight_administration,
)

urlpatterns = [
    path(
        route='users/',
        view=user_list,
        name='user_list'
    ),
    path('users/register/', 
         view=user_register, 
         name='user_register'
    ),
    path('users/login/', 
         view=user_login, 
         name='user_login'),
    path(
        route='planes/',
        view=plane_list,
        name='plane_list'
    ),
    path(
        route='planes/details/<int:plane_id>',
        view=plane_detail,
        name='plane_detail'
    ),
    path(
        route='flights/',
        view=flight_list,
        name='flight_list',
    ),
    path(
        route='flights/flight_administration/',
        view=flight_administration,
        name='flight_administration',
    )
]
