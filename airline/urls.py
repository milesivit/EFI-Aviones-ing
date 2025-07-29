from django.urls import path

from airline.views import (
    user_list,
    plane_list,
    user_list,
    user_register,
    user_login

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
]
