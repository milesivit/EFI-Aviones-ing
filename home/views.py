from django.shortcuts import render, redirect
from django.views import View

class HomeView(View):
    def get(self, request):
        return render(request, 'index.html')

class DevelopersView(View):
    def get(self, request):
        return render(request, 'dev.html')