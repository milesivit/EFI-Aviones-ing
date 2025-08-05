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
    def delete(flght_status: FlightStatus) -> bool:
        """
        Elimina una instancia de FlightStatus.

        Args:
            flght_status (FlightStatus): Instancia del estado de vuelo a eliminar.

        Returns:
            bool: True si la eliminación fue exitosa.

        Raises:
            ValueError: Si la instancia no existe.
        
        Observación:
            - `True()` está mal, debería ser simplemente `True` (sin paréntesis).
            - El error que captura es innecesario porque `.delete()` sobre una instancia no lanza `DoesNotExist`.
        """
        try:
            flght_status.delete()
            return True  # Corregido: era `True()`
        except FlightStatus.DoesNotExist:
            raise ValueError("El estado de vuelo no existe")
        
    @staticmethod
    def update(flight_status: FlightStatus, stauts: str) -> FlightStatus:
        """
        Actualiza el estado de una instancia de FlightStatus.

        Args:
            flight_status (FlightStatus): Instancia a modificar.
            stauts (str): Nuevo valor del estado.

        Returns:
            FlightStatus: Instancia actualizada.

        Observación:
            - Hay un typo: `stauts` debería ser `status`.
        """
        flight_status.status = stauts  # Debería ser `status`
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
