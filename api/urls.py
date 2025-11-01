from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import (
    FlightViewSet,
    FlightAvailableListAPIView,
    FlightDetailAPIView,
    FlightFilterAPIView,
    PassengerViewSet,
    PassengerDetailAPIView,
    ReservationByPassengerAPIView,
    CreateReservationAPIView,
    AvailableSeatsListAPIView,
    PlaneLayoutAPIView,
    SeatAvailabilityAPIView,
    GenerateTicketAPIView,
    TicketInformationAPIView,
    PassengersByFlightAPIView,
    ActiveReservationsByPassengerAPIView,
    PlaneViewSet,
    ChangeReservationStatusAPIView,
    UserViewSet,
    FlightStatusViewSet,
    ReservationViewSet,
    TicketViewSet,
)

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

router = DefaultRouter()
router.register("flight-vs", FlightViewSet, basename="flight-vs")
router.register("passenger-vs", PassengerViewSet, basename="passenger-vs")
router.register("plane-vs", PlaneViewSet, basename="plane-vs")
router.register("user-vs", UserViewSet, basename="user-vs")
router.register("flightStatus-vs", FlightStatusViewSet, basename="flightStatus-vs")
router.register("reservation-vs", ReservationViewSet, basename="reservation-vs")
router.register("ticket-vs", TicketViewSet, basename="ticket-vs")

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
    path(
        "reservationsByPassenger/<int:passenger_id>/",
        ReservationByPassengerAPIView.as_view(),
        name="reservations-by-passenger",
    ),
    path(
        "createReservation/",
        CreateReservationAPIView.as_view({"post": "create"}),
        name="create-reservation",
    ),
    path(
        "changeReservationStatus/<int:reservation_id>/",
        ChangeReservationStatusAPIView.as_view(),
        name="change-reservation-status",
    ),
    path(
        "availableSeats/<int:flight_id>/",
        AvailableSeatsListAPIView.as_view(),
        name="available-seats",
    ),
    path(
        "planeLayout/<int:plane_id>/", PlaneLayoutAPIView.as_view(), name="plane-layout"
    ),
    path(
        "checkSeatAvailability/<int:plane_id>/<str:seat_code>/",
        SeatAvailabilityAPIView.as_view(),
        name="seat-availability",
    ),
    path(
        "generateTicket/<int:reservation_id>",
        GenerateTicketAPIView.as_view(),
        name="generate-ticket",
    ),
    path(
        "ticketInformation/<str:barcode>",
        TicketInformationAPIView.as_view(),
        name="ticket-information",
    ),
    path(
        "passengersByFlight/<int:flight_id>",
        PassengersByFlightAPIView.as_view(),
        name="passenger-flight",
    ),
    path(
        "activeReservations/<int:passenger_id>",
        ActiveReservationsByPassengerAPIView.as_view(),
        name="active-reservation",
    ),
    # YOUR PATTERNS
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    # Optional UI:
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
