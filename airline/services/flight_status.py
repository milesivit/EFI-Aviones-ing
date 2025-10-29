from airline.models import FlightStatus #esta bien el modelo aca ya que El Service solo recibe o devuelve objetos y llama al Repository para hacer el trabajo real.
from airline.repositories.flight_status import FlightStatusRepository


class FlightStatusService:
    @staticmethod
    def create(status: str):
        return FlightStatus.objects.create(status=status)

    @staticmethod
    def delete(flight_status_id: int) -> bool:
        flight_status = FlightStatusRepository.get_by_id(
            flight_status_id=flight_status_id
        )
        if flight_status:
            return FlightStatusRepository.delete(flight_status=flight_status)
        return False

    @staticmethod
    def update(
        flight_status: FlightStatus,
        status: str,
    ) -> FlightStatus:
        flight_status.status = status
        return flight_status

    @staticmethod
    def get_all() -> list[FlightStatus]:
        return FlightStatusRepository.get_all()

    @staticmethod
    def get_by_id(flight_status_id: int) -> list[FlightStatus]:
        if flight_status_id:
            return FlightStatusRepository.get_by_id(flight_status_id=flight_status_id)
        return ValueError("El Estado de Vuelo No Existe")
