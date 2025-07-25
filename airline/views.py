from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, DeleteView, UpdateView
from airline.models import User
from airline.services.user import UserService
from airline.services.plane import PlaneService


# Función para listar usuarios
def user_list(request):
    users = UserService.get_all()
    return render(request, 'users/list.html', {'users': users})

# Función para listar aviones
def plane_list(request):
    airplanes = PlaneService.get_all()  
    return render(request, 'plane/list.html', {'airplanes': airplanes})

