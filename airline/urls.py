from django.urls import path

from airline.views import (
    user_list,
    user_detail,
    UserCreateView,
    UserDeleteView,
    UserUpdateView,
)

urlpatterns = [
    path(
        route='users/',
        view=user_list,
        name='user_list'
    )
]
