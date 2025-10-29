from airline.models import FlightStatus


class FlightStatusRepository:
    """
    Repositorio para manipular objetos FlightStatus (Estados de Vuelo) en la base de datos.
    Contiene métodos estáticos para realizar operaciones CRUD (crear, leer, actualizar, eliminar).
    """

    @staticmethod
    def create(status: str) -> FlightStatus:
        """
        Crea un nuevo estado de vuelo en la base de datos.

        Args:
            status (str): Estado del vuelo a crear (por ejemplo: "Programado", "Cancelado", etc.).

        Returns:
            FlightStatus: Instancia creada del modelo FlightStatus.
        """
        flight_status = FlightStatus.objects.create(status=status)
        return flight_status

    @staticmethod
    def delete(flight_status: FlightStatus) -> bool:
        """
        elimina una instancia de flightstatus
        """
        flight_status.delete()
        return True


    @staticmethod
    def update(flight_status: FlightStatus, status: str) -> FlightStatus:
        """
        actualiza una instancia de flightstatus
        """
        flight_status.status = status
        flight_status.save()
        return flight_status


    @staticmethod
    def get_all() -> list[FlightStatus]:
        """
        Recupera todos los registros de estados de vuelo.

        Returns:
            list[FlightStatus]: Lista de todas las instancias.
        """
        return FlightStatus.objects.all()

    @staticmethod
    def get_by_id(flight_status_id: int) -> FlightStatus:
        """
        Busca una instancia por su ID.

        Args:
            flight_status_id (int): ID del estado de vuelo.

        Returns:
            FlightStatus | None: Instancia si existe, None si no.
        """
        try:
            return FlightStatus.objects.get(id=flight_status_id)
        except FlightStatus.DoesNotExist:
            return None

    @staticmethod
    def get_by_status(status: str) -> list[FlightStatus]:
        """
        Filtra estados de vuelo que contenga una cadena determinada (búsqueda parcial).

        Args:
            status (str): Parte del estado a buscar.

        Returns:
            list[FlightStatus]: Lista de coincidencias.
        """
        return FlightStatus.objects.filter(status__icontains=status)
