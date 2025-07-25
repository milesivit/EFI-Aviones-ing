from django.urls import path

from airline.views import (
    user_list,
    plane_list

)

urlpatterns = [
    path(
        route='users/',
        view=user_list,
        name='user_list'
    ),
    path(
        route='planes/',
        view=plane_list,
        name='plane_list'
    )
]
