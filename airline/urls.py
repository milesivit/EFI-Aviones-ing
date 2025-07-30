from django.urls import path

from airline.views import (
    user_list,
    plane_list,
    user_register,
    user_login,
    flight_list,

)

urlpatterns = [
    path(
        route='users/',
        view=user_list,
        name='user_list'
    ),
    path('users/register/', 
         view=user_register, 
         name='user_register'),
    path('users/login/', 
         view=user_login, 
         name='user_login'),
    path(
        route='planes/',
        view=plane_list,
        name='plane_list'
    ),
    path(
        route='flights/',
        view=flight_list,
        name='flight_list',
    ),
]
