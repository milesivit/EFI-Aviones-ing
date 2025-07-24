from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, DeleteView, UpdateView
from airline.models import User
from airline.services.user import UserService


# Función para listar usuarios
def user_list(request):
    users = UserService.get_all()
    return render(request, 'users/list.html', {'users': users})


# Función para detalle usuario
def user_detail(request, user_id):
    user = UserService.get_by_id(user_id)
    if not user:
        messages.error(request, 'Usuario no encontrado')
        return redirect('user_list')
    return render(request, 'users/detail.html', {'user': user})


# Crear usuario - vista basada en clase simple
class UserCreateView(View):
    def get(self, request):
        return render(request, 'users/create.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        role = request.POST.get('role')

        # Validaciones básicas
        if not username or not password or not email or not role:
            messages.error(request, 'Todos los campos son obligatorios')
            return render(request, 'users/create.html')

        UserService.create(username=username, password=password, email=email, role=role)
        messages.success(request, 'Usuario creado con éxito')
        return redirect('user_list')


# Borrar usuario con DeleteView genérica
class UserDeleteView(DeleteView):
    model = User
    template_name = 'users/delete.html'
    pk_url_kwarg = 'user_id'
    success_url = reverse_lazy('user_list')


# Actualizar usuario con UpdateView
from django import forms

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'role']


class UserUpdateView(UpdateView):
    model = User
    form_class = UserForm
    template_name = 'users/update.html'
    pk_url_kwarg = 'user_id'
    success_url = reverse_lazy('user_list')

    def form_valid(self, form):
        messages.success(self.request, 'Usuario actualizado con éxito')
        return super().form_valid(form)
