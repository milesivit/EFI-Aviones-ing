from django.shortcuts import render, redirect  # Funciones para renderizar plantillas y redirigir
from django.views import View  # Clase base para vistas basadas en clases (CBV)
from django.contrib.auth import logout  # Función para cerrar sesión de usuarios

# Vista para la página de inicio
class HomeView(View):
    def get(self, request):
        # Renderiza la plantilla "index.html" cuando se accede por GET
        return render(request, "index.html")


# Vista para la página de desarrolladores
class DevelopersView(View):
    def get(self, request):
        # Renderiza la plantilla "dev.html" cuando se accede por GET
        return render(request, "dev.html")


# Vista para cerrar sesión de usuario
class LogoutView(View):
    def get(self, request):
        # Cierra la sesión del usuario actual
        logout(request)
        # Redirige a la página de login después de cerrar sesión
        return redirect("user_login")
