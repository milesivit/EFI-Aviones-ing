from airline.models import Flight
from airline.repositories.flight import FlightRepository

from datetime import datetime, timedelta

class FlightService:
    @staticmethod
    def create(
        origin: str,
        destination: str,
        departure_date: datetime,
        arrival_date: datetime,
        duration: timedelta,
        status: str,
        base_price: float,
        plane_id: int,
        user_id: list[int],
    ):
        return FlightRepository.create(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            arrival_date=arrival_date,
            duration=duration,
            status=status,
            base_price=base_price,
            plane_id=plane_id,
            user_id=user_id,
        )

    @staticmethod
    def delete(flight_id: int) -> bool:
        flight = FlightRepository.get_by_id(flight_id=flight_id)
        if flight:
            return FlightRepository.delete(flight=flight)
        return False
    
    @staticmethod
    def update(
        flight: Flight,
        origin: str,
        destination: str,
        departure_date: datetime,
        arrival_date: datetime,
        duration: timedelta,
        status: str,
        base_price: float,
        plane_id: int,
        user_ids: list[int],
    ) -> Flight:
        flight.origin = origin
        flight.destination = destination
        flight.departure_date = departure_date
        flight.arrival_date = arrival_date
        flight.duration = duration
        flight.status = status
        flight.base_price = base_price
        flight.plane_id = plane_id
        flight.user_id.set(user_ids) 
        flight.save()
        return flight


    @staticmethod
    def get_all() -> list[Flight]:
        return FlightRepository.get_all() 
    
    @staticmethod
    def get_by_id(flight_id: int) -> list[Flight]:
        if flight_id:
            return FlightRepository.get_by_id(flight_id=flight_id)
        return ValueError("El Vuelo No Existe")
    
    @staticmethod
    def search_by_origin(origin: str) -> list[Flight]:
        if origin:
            return FlightRepository.search_by_origin(origin=origin)
        return ValueError("El Origen No Existe")