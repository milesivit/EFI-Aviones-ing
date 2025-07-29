from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import logout

class HomeView(View):
    def get(self, request):
        return render(request, 'index.html')

class DevelopersView(View):
    def get(self, request):
        return render(request, 'dev.html')


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('user_login')