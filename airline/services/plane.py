from airline.models import Plane #esta bien el modelo aca ya que El Service solo recibe o devuelve objetos y llama al Repository para hacer el trabajo real.
from airline.repositories.plane import PlaneRepository


class PlaneService:

    @staticmethod
    def create(
        model: str,
        capacity: int,
        rows: int,
        columns: int,
    ) -> Plane:
        return PlaneRepository.create(
            model=model,
            capacity=capacity,
            rows=rows,
            columns=columns,
        )

    @staticmethod
    def delete(plane_id: int) -> bool:
        plane = PlaneRepository.get_by_id(plane_id=plane_id)
        if plane:
            return PlaneRepository.delete(plane=plane)
        return False

    @staticmethod
    def update(
        plane_id: int,
        model: str,
        capacity: int,
        rows: int,
        columns: int,
    ) -> Plane: 
        plane = PlaneRepository.get_by_id(plane_id=plane_id)
        if plane:
            return PlaneRepository.update(
                plane=plane,
                model=model,
                capacity=capacity,
                rows=rows,
                columns=columns,
            )
        raise ValueError("El avión no existe")  # opcional: manejar caso no encontrado


    @staticmethod
    def get_all() -> list[Plane]:
        return PlaneRepository.get_all()

    @staticmethod
    def get_by_id(plane_id: int) -> list[Plane]:
        if plane_id:
            return PlaneRepository.get_by_id(plane_id=plane_id)
        return ValueError("El Avion No Existe")

    @staticmethod
    def search_by_model(model: str) -> list[Plane]:
        if model:
            return PlaneRepository.search_by_model(model=model)
        return ValueError("El Avion No Existe")
    
    @staticmethod
    def get_plane_layout(plane_id: int):
        plane = PlaneRepository.get_plane_by_id(plane_id)
        if not plane:
            return None  

        seats = PlaneRepository.get_seats_by_plane(plane)

        layout = []
        for r in range(1, plane.rows + 1):
            row_seats = seats.filter(row=r)
            layout.append([
                {
                    "number": seat.number,
                    "seat_type": seat.seat_type,
                    "status": seat.status,
                }
                for seat in row_seats
            ])

        return {
            "plane": str(plane),
            "rows": plane.rows,
            "columns": plane.columns,
            "layout": layout,
        }