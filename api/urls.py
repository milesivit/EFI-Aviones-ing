from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import FlightViewSet, FlightAvailableListAPIView, FlightDetailAPIView, FlightFilterAPIView

router = DefaultRouter()
router.register('flight-vs', FlightViewSet, basename='flight-vs')

urlpatterns = [
    path('', include(router.urls)),
    path('flightAvailable/', FlightAvailableListAPIView.as_view(), name='flight-available'),
    path('flightDetail/<int:pk>/', FlightDetailAPIView.as_view(), name='flight-detail'),
    path("flightFilter/", FlightFilterAPIView.as_view(), name="flight-filter"),
]
