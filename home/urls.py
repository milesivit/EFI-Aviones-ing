from django.urls import path
from home.views import (
    HomeView,
    DevelopersView
    )

urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('dev/', DevelopersView.as_view(), name='dev'),
]

