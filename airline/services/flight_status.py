from airline.models import FlightStatus
from airline.repositories.flight_status import FlightStatusRepository

class FlightStatusService:
    @staticmethod
    def create(status: str):
          return FlightStatus.objects.create(status=status)
    
    @staticmethod
    def delete(flight_status_id: int) -> bool:
        flight_status = FlightStatusRepository.get_by_id(flight_status_id=flight_status_id)
        if flight_status:
            return FlightStatusRepository.delete(flight_status=flight_status)
        return False
    
    @staticmethod
    def update(
        flight_stauts: FlightStatus,
        status: str,
    ) -> FlightStatus:
        flight_stauts.status = status
        return flight_stauts
    
    @staticmethod
    def get_all() -> list[FlightStatus]:
        return FlightStatusRepository.get_all()
    
    @staticmethod
    def get_by_id(flight_status_id: int) -> list[FlightStatus]:
        if flight_status_id:
            return FlightStatusRepository.get_by_id(flight_status_id=flight_status_id)
        return ValueError("El Estado de Vuelo No Existe")
    
    @staticmethod
    def search(status: str) -> list[FlightStatus]:
        if status:
            return FlightStatusRepository.search_by_satuts(origin=origin)
        return ValueError("El Estado de Vuelo No Existe")