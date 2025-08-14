from django.urls import path  # Importa la función path para definir rutas en Django
from home.views import (
    HomeView,        # Vista de la página de inicio
    DevelopersView,  # Vista de la página de desarrolladores
    LogoutView,      # Vista para cerrar sesión
)

# Lista de rutas URL de la aplicación "home"
urlpatterns = [
    # Ruta raíz ("/") que muestra la página de inicio
    path("", HomeView.as_view(), name="index"),

    # Ruta "/dev/" que muestra la página de desarrolladores
    path("dev/", DevelopersView.as_view(), name="dev"),

    # Ruta "/logout/" que cierra la sesión del usuario
    path("logout/", LogoutView.as_view(), name="logout"),
]
