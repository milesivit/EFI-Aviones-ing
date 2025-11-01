# Importamos pytest para manejar los tests
import pytest

# Importamos reverse para poder construir URLs dinámicamente en los tests
from django.urls import reverse

# Importamos el modelo User desde la app airline
from airline.models import User
from rest_framework.test import APIClient


@pytest.fixture
def admin_client(db):
    user = User.objects.create_superuser(
        username="admin", email="admin@test.com", password="admin123"
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client


# -------------------- TEST: Crear un nuevo usuario --------------------
@pytest.mark.django_db
def test_create_user(admin_client):
    # Definimos el payload (datos que se envían en el body del POST)
    payload = {
        "username": "new_user",
        "email": "new_user@test.com",
        "password": "123456",
        "role": "user",
    }

    # Construimos la URL del endpoint de creación
    url = reverse("user-vs-list")

    # Enviamos la petición POST con el payload en formato JSON
    response = admin_client.post(url, payload, format="json")
    # Parseamos la respuesta a JSON
    body = response.json()

    # Buscamos el usuario creado en la base de datos
    user = User.objects.get(username="new_user")

    # Verificamos que el servidor haya respondido con 201 (creado)
    assert response.status_code == 201
    # Comprobamos que los datos coincidan
    assert body["username"] == user.username
    assert body["email"] == user.email
    assert body["role"] == user.role
    # Confirmamos que la contraseña se haya guardado correctamente (encriptada)
    assert user.check_password("123456")


# -------------------- TEST: Crear usuario con email inválido --------------------
@pytest.mark.django_db
def test_create_user_invalid_email(admin_client):
    # Intentamos crear un usuario con un email inválido
    payload = {
        "username": "user_invalid",
        "email": "not-an-email",
        "password": "123456",
        "role": "user",
    }

    # Endpoint de creación
    url = reverse("user-vs-list")

    # Petición POST con email inválido
    response = admin_client.post(url, payload, format="json")
    body = response.json()

    # Esperamos un error 400 (Bad Request)
    assert response.status_code == 400
    # Verificamos que el campo email aparezca en los errores
    assert "email" in body


# -------------------- TEST: Obtener un usuario específico --------------------
@pytest.mark.django_db
def test_user_retrieve(admin_client):
    # Creamos un usuario de prueba
    user = User.objects.create_user(
        username="user1", email="u1@test.com", password="123"
    )

    # Construimos la URL con el ID del usuario (detalle)
    url = reverse("user-vs-detail", args=[user.pk])

    # Realizamos la petición GET para obtenerlo
    response = admin_client.get(url)
    body = response.json()

    # Verificamos que la respuesta sea exitosa
    assert response.status_code == 200
    # Comprobamos que los datos devueltos sean correctos
    assert body["username"] == user.username
    assert body["email"] == user.email
    assert body["role"] == user.role


# -------------------- TEST: Actualizar usuario con PUT --------------------
@pytest.mark.django_db
def test_user_update_put(admin_client):
    # Creamos un usuario de prueba
    user = User.objects.create_user(
        username="user1", email="u1@test.com", password="123"
    )

    # Definimos un payload con los nuevos datos
    payload = {
        "username": "user1",
        "email": "u1_new@test.com",
        "password": "123",
        "role": "admin",
    }

    # Construimos la URL con el ID del usuario
    url = reverse("user-vs-detail", args=[user.pk])

    # Enviamos una petición PUT (reemplaza todos los campos)
    response = admin_client.put(url, payload, format="json")

    # Actualizamos la instancia desde la base de datos
    user.refresh_from_db()

    # Verificamos que la actualización haya sido exitosa
    assert response.status_code == 200
    assert user.email == "u1_new@test.com"
    assert user.role == "admin"


# -------------------- TEST: Actualizar usuario con PATCH --------------------
@pytest.mark.django_db
def test_user_update_patch(admin_client):
    # Creamos un usuario inicial
    user = User.objects.create_user(
        username="user1", email="u1@test.com", password="123"
    )

    # Enviamos solo el campo que queremos modificar (role)
    payload = {"role": "admin"}

    # URL del detalle del usuario
    url = reverse("user-vs-detail", args=[user.pk])

    # Petición PATCH (actualización parcial)
    response = admin_client.patch(url, payload, format="json")

    # Refrescamos el usuario para obtener los cambios
    user.refresh_from_db()

    # Verificamos que el cambio se haya aplicado correctamente
    assert response.status_code == 200
    assert user.role == "admin"
