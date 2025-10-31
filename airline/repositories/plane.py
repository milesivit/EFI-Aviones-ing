from airline.models import Plane, Seat


class PlaneRepository:
    """
    Clase de repositorio que se encargará de conectarse con la base de datos
    para manipular aviones.
    """

    @staticmethod
    def create(
        model: str,
        capacity: int,
        rows: int,
        columns: int,
    ) -> Plane:
        """
        Crea un nuevo avión.

        Args:
            model: Modelo del avión.
            capacity: Capacidad total.
            rows: Número de filas de asientos.
            columns: Número de columnas de asientos.

        Returns:
            Instancia del avión creado.
        """
        return Plane.objects.create(
            model=model,
            capacity=capacity,
            rows=rows,
            columns=columns,
        )

    @staticmethod
    def delete(plane: Plane) -> bool:
        """
        Elimina un avión.

        Args:
            plane: Instancia del avión a eliminar.

        Returns:
            True si se elimina correctamente.

        Raises:
            ValueError: Si el avión no existe.
        """
        try:
            plane.delete()
        except Plane.DoesNotExist:
            raise ValueError("El Avión No Existe")

    @staticmethod
    def update(
        plane: Plane, model: str, capacity: int, rows: int, columns: int
    ) -> Plane:
        """
        Actualiza los datos de un avión.

        Args:
            plane: Instancia del avión a actualizar.
            model: Nuevo modelo.
            capacity: Nueva capacidad.
            rows: Nuevas filas.
            columns: Nuevas columnas.

        Returns:
            Instancia del avión actualizada.
        """
        plane.model = model
        plane.capacity = capacity
        plane.rows = rows
        plane.columns = columns
        plane.save()

        return plane

    @staticmethod
    def get_all() -> list[Plane]:
        """
        Obtiene todos los objetos (aviones).

        Returns:
            Lista de todos los aviones.
        """
        return Plane.objects.all()

    @staticmethod
    def get_by_id(plane_id: int) -> Plane:
        """
        Obtiene un avión a partir de su ID.

        Args:
            plane_id: ID del avión.

        Returns:
            Instancia del avión o None si no existe.
        """
        try:
            return Plane.objects.get(id=plane_id)
        except Plane.DoesNotExist:
            return None

    @staticmethod
    def search_by_model(model: str) -> list[Plane]:
        """
        Busca los aviones cuyo modelo contenga el texto ingresado.

        Args:
            model: Texto parcial o completo del modelo a buscar.

        Returns:
            Lista de aviones coincidentes o None si no se encuentran.
        """
        try:
            return Plane.objects.filter(model__icontains=model)
        except Plane.DoesNotExist:
            return None
        
    @staticmethod
    def get_plane_by_id(plane_id: int) -> Plane | None:
        try:
            return Plane.objects.get(pk=plane_id)
        except Plane.DoesNotExist:
            return None

    @staticmethod
    def get_seats_by_plane(plane: Plane):
        return Seat.objects.filter(plane=plane).order_by("row", "column")
