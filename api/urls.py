from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import (
    FlightViewSet,
    FlightAvailableListAPIView,
    FlightDetailAPIView,
    FlightFilterAPIView,
    PassengerViewSet,
    PassengerDetailAPIView,
    ReservationByPassengerAPIView
)

router = DefaultRouter()
router.register("flight-vs", FlightViewSet, basename="flight-vs")
router.register("passenger-vs", PassengerViewSet, basename="passenger-vs")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "flightAvailable/",
        FlightAvailableListAPIView.as_view(),
        name="flight-available",
    ),
    path("flightDetail/<int:pk>/", FlightDetailAPIView.as_view(), name="flight-detail"),
    path("flightFilter/", FlightFilterAPIView.as_view(), name="flight-filter"),
    path(
        "passengerDetail/<int:pk>/",
        PassengerDetailAPIView.as_view(),
        name="passenger-detail",
    ),
     path('reservationsByPassenger/<int:passenger_id>/', ReservationByPassengerAPIView.as_view(), name='reservations-by-passenger'),
]
