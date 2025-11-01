# -------------------- IMPORTS --------------------
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from airline.models import Plane, User


# -------------------- FIXTURE: Cliente autenticado como admin --------------------
@pytest.fixture
def admin_client(db):
    """
    Crea un superusuario y un cliente autenticado para realizar peticiones
    con permisos de administrador.
    """
    admin_user = User.objects.create_superuser(
        username="admin",
        email="admin@test.com",
        password="admin123"
    )
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


# -------------------- TEST: Crear un avión --------------------
@pytest.mark.django_db
def test_create_plane(admin_client):
    """
    Verifica que se pueda crear un avión correctamente mediante POST.
    """
    payload = {
        "model": "Boeing 737",
        "capacity": 180,
        "rows": 30,
        "columns": 6
    }

    url = reverse("plane-vs-list")
    response = admin_client.post(url, payload, format="json")
    body = response.json()

    # Obtenemos el avión desde la base de datos
    plane = Plane.objects.get(model="Boeing 737")

    assert response.status_code == 201
    assert body["model"] == plane.model
    assert body["capacity"] == plane.capacity
    assert body["rows"] == plane.rows
    assert body["columns"] == plane.columns


# -------------------- TEST: Obtener todos los aviones --------------------
@pytest.mark.django_db
def test_get_all_planes(admin_client):
    """
    Verifica que se obtengan correctamente todos los aviones registrados.
    """
    Plane.objects.create(model="Airbus A320", capacity=150, rows=25, columns=6)
    Plane.objects.create(model="Boeing 747", capacity=366, rows=61, columns=6)

    url = reverse("plane-vs-list") + "?page_size=100"
    response = admin_client.get(url)
    body = response.json()

    assert response.status_code == 200
    assert body["count"] >= 2
    assert len(body["results"]) >= 2

    models = [p["model"] for p in body["results"]]
    assert "Airbus A320" in models
    assert "Boeing 747" in models


# -------------------- TEST: Obtener un avión específico --------------------
@pytest.mark.django_db
def test_plane_retrieve(admin_client):
    """
    Verifica que se pueda obtener un avión en particular mediante GET.
    """
    plane = Plane.objects.create(model="Embraer 190", capacity=100, rows=20, columns=5)
    url = reverse("plane-vs-detail", args=[plane.pk])

    response = admin_client.get(url)
    body = response.json()

    assert response.status_code == 200
    assert body["model"] == plane.model
    assert body["capacity"] == plane.capacity
    assert body["rows"] == plane.rows
    assert body["columns"] == plane.columns


# -------------------- TEST: Actualizar un avión (PUT) --------------------
@pytest.mark.django_db
def test_plane_update_put(admin_client):
    """
    Verifica que se pueda actualizar un avión con PUT (todos los campos).
    """
    plane = Plane.objects.create(model="Boeing 737", capacity=180, rows=30, columns=6)

    payload = {
        "model": "Boeing 737 MAX",
        "capacity": 200,
        "rows": 33,
        "columns": 6
    }

    url = reverse("plane-vs-detail", args=[plane.pk])
    response = admin_client.put(url, payload, format="json")

    plane.refresh_from_db()

    assert response.status_code == 200
    assert plane.model == "Boeing 737 MAX"
    assert plane.capacity == 200
    assert plane.rows == 33


# -------------------- TEST: Actualizar un avión parcialmente (PATCH) --------------------
@pytest.mark.django_db
def test_plane_update_patch(admin_client):
    """
    Verifica que se pueda modificar un campo de un avión con PATCH.
    """
    plane = Plane.objects.create(model="Boeing 787", capacity=242, rows=40, columns=6)

    payload = {"capacity": 250}

    url = reverse("plane-vs-detail", args=[plane.pk])
    response = admin_client.patch(url, payload, format="json")

    plane.refresh_from_db()

    assert response.status_code == 200
    assert plane.capacity == 250


# -------------------- TEST: Eliminar un avión --------------------
@pytest.mark.django_db
def test_plane_delete(admin_client):
    """
    Verifica que se pueda eliminar un avión mediante DELETE.
    """
    plane = Plane.objects.create(model="Boeing 757", capacity=239, rows=40, columns=6)
    url = reverse("plane-vs-detail", args=[plane.pk])

    response = admin_client.delete(url)

    assert response.status_code in [200, 204]
    assert not Plane.objects.filter(pk=plane.pk).exists()
