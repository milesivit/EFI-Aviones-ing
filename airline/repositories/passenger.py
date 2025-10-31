from datetime import date
from airline.models import Passenger, Reservation


class PassengerRepository:
    """
    Repositorio para manipular objetos Passenger (pasajeros) en la base de datos.
    """

    @staticmethod
    def create(
        name: str,
        document: str,
        document_type: str,
        email: str,
        phone: str,
        birth_date: date,
    ) -> Passenger:
        """
        Crea un nuevo pasajero.

        Args:
            name: Nombre del pasajero.
            document: Documento de identidad.
            document_type: Tipo de documento (DNI, pasaporte, etc.).
            email: Correo electrónico.
            phone: Número de teléfono.
            birth_date: Fecha de nacimiento.

        Returns:
            Instancia del pasajero creado.
        """
        return Passenger.objects.create(
            name=name,
            document=document,
            document_type=document_type,
            email=email,
            phone=phone,
            birth_date=birth_date,
        )

    @staticmethod
    def delete(passenger: Passenger) -> bool:
        """
        Elimina un pasajero.

        Args:
            passenger: Instancia del pasajero a eliminar.

        Returns:
            True si se eliminó correctamente.

        Raises:
            ValueError: Si el pasajero no existe.
        """
        try:
            passenger.delete()
            return True
        except Passenger.DoesNotExist:
            raise ValueError("El pasajero no existe")

    @staticmethod
    def update(
        passenger: Passenger,
        name: str,
        document: str,
        document_type: str,
        email: str,
        phone: str,
        birth_date: date,
    ) -> Passenger:
        """
        Actualiza la información de un pasajero.

        Args:
            passenger: Instancia del pasajero a actualizar.
            name: Nuevo nombre.
            document: Nuevo documento.
            document_type: Nuevo tipo de documento.
            email: Nuevo email.
            phone: Nuevo teléfono.
            birth_date: Nueva fecha de nacimiento.

        Returns:
            Pasajero actualizado.
        """
        passenger.name = name
        passenger.document = document
        passenger.document_type = document_type
        passenger.email = email
        passenger.phone = phone
        passenger.birth_date = birth_date
        passenger.save()
        return passenger

    @staticmethod
    def get_all() -> list[Passenger]:
        """
        Obtiene todos los pasajeros.

        Returns:
            Lista de todos los pasajeros.
        """
        return Passenger.objects.all()

    @staticmethod
    def get_by_id(passenger_id: int) -> Passenger:
        """
        Obtiene un pasajero por su ID.

        Args:
            passenger_id: ID del pasajero.

        Returns:
            Instancia del pasajero o None si no existe.
        """
        try:
            return Passenger.objects.get(id=passenger_id)
        except Passenger.DoesNotExist:
            return None

    @staticmethod
    def search_by_name(name: str) -> list[Passenger]:
        """
        Busca pasajeros por nombre (búsqueda parcial, insensible a mayúsculas).

        Args:
            name: Nombre a buscar.

        Returns:
            Lista de pasajeros cuyo nombre contenga el texto buscado.
        """
        return Passenger.objects.filter(name__icontains=name)
    
    @staticmethod
    def get_passenger_by_id(passenger_id: int) -> Passenger | None:
        try:
            return Passenger.objects.get(pk=passenger_id)
        except Passenger.DoesNotExist:
            return None

    @staticmethod
    def get_active_reservations(passenger: Passenger):
        return Reservation.objects.filter(passenger=passenger, status="confirmed")
