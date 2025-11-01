import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from airline.models import Flight, FlightStatus, Plane, User
from datetime import datetime
from django.utils import timezone


# -------------------- FIXTURE: Cliente autenticado como admin --------------------
@pytest.fixture
def admin_client(db):
    """
    Crea un superusuario autenticado para las pruebas.
    """
    admin_user = User.objects.create_superuser(
        username="admin", email="admin@test.com", password="admin123"
    )
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


# -------------------- FIXTURE: Datos relacionados para crear vuelos --------------------
@pytest.fixture
def flight_dependencies(db):
    """
    Crea objetos relacionados requeridos por Flight:
    - Un estado de vuelo (FlightStatus)
    - Un avión (Plane)
    - Un usuario pasajero
    """
    status = FlightStatus.objects.create(status="Scheduled")
    plane = Plane.objects.create(model="Boeing 737", capacity=180, rows=30, columns=6)
    passenger = User.objects.create_user(
        username="passenger1", email="p1@test.com", password="123"
    )
    return {"status": status, "plane": plane, "user": passenger}


# -------------------- TEST: Crear vuelo --------------------
@pytest.mark.django_db
def test_create_flight(admin_client, flight_dependencies):
    """
    Verifica que se pueda crear un vuelo correctamente mediante POST.
    """

    departure = timezone.make_aware(datetime(2025, 12, 1, 10, 0))
    arrival = timezone.make_aware(datetime(2025, 12, 1, 14, 0))
    duration = arrival - departure

    url = reverse("flight-vs-list")
    payload = {
        "origin": "Buenos Aires",
        "destination": "Madrid",
        "departure_date": departure,
        "arrival_date": arrival,
        "duration": duration,
        "base_price": 1500.00,
        "status": flight_dependencies["status"].id,
        "plane": flight_dependencies["plane"].id,
        "user": [flight_dependencies["user"].id],
    }

    response = admin_client.post(url, payload, format="json")
    body = response.json()

    flight = Flight.objects.get(origin="Buenos Aires")

    assert response.status_code == 201
    assert body["origin"] == flight.origin
    assert body["destination"] == flight.destination
    assert flight.plane.id == flight_dependencies["plane"].id
    assert flight.status.id == flight_dependencies["status"].id


# -------------------- TEST: Obtener todos los vuelos --------------------
@pytest.mark.django_db
def test_get_all_flights(admin_client, flight_dependencies):
    """
    Verifica que se obtengan correctamente todos los vuelos registrados.
    """
    departure = timezone.make_aware(datetime(2025, 12, 1, 10, 0))
    arrival = timezone.make_aware(datetime(2025, 12, 1, 14, 0))
    duration = arrival - departure

    Flight.objects.create(
        origin="Buenos Aires",
        destination="Miami",
        departure_date=departure,
        arrival_date=arrival,
        duration=duration,
        base_price=1200.00,
        status=flight_dependencies["status"],
        plane=flight_dependencies["plane"],
    )

    Flight.objects.create(
        origin="Londres",
        destination="Tokio",
        departure_date=departure,
        arrival_date=arrival,
        duration=duration,
        base_price=2000.00,
        status=flight_dependencies["status"],
        plane=flight_dependencies["plane"],
    )

    url = reverse("flight-vs-list")
    response = admin_client.get(url)
    body = response.json()

    assert response.status_code == 200
    assert body["count"] >= 2
    origins = [f["origin"] for f in body["results"]]
    assert "Buenos Aires" in origins
    assert "Londres" in origins


# -------------------- TEST: Actualizar vuelo (PUT) --------------------
@pytest.mark.django_db
def test_flight_update_put(admin_client, flight_dependencies):
    """
    Verifica que se pueda actualizar un vuelo completamente mediante PUT.
    """
    departure = timezone.make_aware(datetime(2025, 12, 1, 10, 0))
    arrival = timezone.make_aware(datetime(2025, 12, 1, 14, 0))
    duration = arrival - departure

    flight = Flight.objects.create(
        origin="Madrid",
        destination="Lisboa",
        departure_date=departure,
        arrival_date=arrival,
        duration=duration,
        base_price=400.00,
        status=flight_dependencies["status"],
        plane=flight_dependencies["plane"],
    )

    payload = {
        "origin": "Madrid",
        "destination": "Barcelona",
        "departure_date": departure,
        "arrival_date": arrival,
        "duration": duration,
        "base_price": 450.00,
        "status": flight_dependencies["status"].id,
        "plane": flight_dependencies["plane"].id,
        "user": [flight_dependencies["user"].id],
    }

    url = reverse("flight-vs-detail", args=[flight.pk])
    response = admin_client.put(url, payload, format="json")

    flight.refresh_from_db()

    assert response.status_code == 200
    assert flight.destination == "Barcelona"
    assert float(flight.base_price) == 450.00


# -------------------- TEST: Actualizar vuelo parcialmente (PATCH) --------------------
@pytest.mark.django_db
def test_flight_update_patch(admin_client, flight_dependencies):
    """
    Verifica que se pueda modificar parcialmente un vuelo con PATCH.
    """
    departure = timezone.make_aware(datetime(2025, 12, 1, 10, 0))
    arrival = timezone.make_aware(datetime(2025, 12, 1, 14, 0))
    duration = arrival - departure

    flight = Flight.objects.create(
        origin="Berlin",
        destination="Amsterdam",
        departure_date=departure,
        arrival_date=arrival,
        duration=duration,
        base_price=350.00,
        status=flight_dependencies["status"],
        plane=flight_dependencies["plane"],
    )

    payload = {"base_price": 380.00}
    url = reverse("flight-vs-detail", args=[flight.pk])
    response = admin_client.patch(url, payload, format="json")

    flight.refresh_from_db()

    assert response.status_code == 200
    assert float(flight.base_price) == 380.00


# -------------------- TEST: Eliminar vuelo --------------------
@pytest.mark.django_db
def test_flight_delete(admin_client, flight_dependencies):
    """
    Verifica que se pueda eliminar un vuelo correctamente mediante DELETE.
    """

    departure = timezone.make_aware(datetime(2025, 12, 1, 10, 0))
    arrival = timezone.make_aware(datetime(2025, 12, 1, 14, 0))
    duration = arrival - departure

    flight = Flight.objects.create(
        origin="Chicago",
        destination="Toronto",
        departure_date=departure,
        arrival_date=arrival,
        duration=duration,
        base_price=700.00,
        status=flight_dependencies["status"],
        plane=flight_dependencies["plane"],
    )

    url = reverse("flight-vs-detail", args=[flight.pk])
    response = admin_client.delete(url)

    assert response.status_code in [200, 204]
    assert not Flight.objects.filter(pk=flight.pk).exists()
