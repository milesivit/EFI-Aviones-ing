from datetime import date
from airline.models import Passenger
from airline.repositories.passenger import PassengerRepository


class PassengerService:

    @staticmethod
    def create(
        name: str,
        document: str,
        document_type: str,
        email: str,
        phone: str,
        birth_date: date,
    ) -> Passenger:
        return PassengerRepository.create(
            name=name,
            document=document,
            document_type=document_type,
            email=email,
            phone=phone,
            birth_date=birth_date,
        )

    @staticmethod
    def delete(passenger_id: int) -> bool:
        passenger = PassengerRepository.get_by_id(passenger_id=passenger_id)
        if passenger:
            return PassengerRepository.delete(passenger=passenger)
        return False

    @staticmethod
    def update(
        passenger_id: int,
        name: str,
        document: str,
        document_type: str,
        email: str,
        phone: str,
        birth_date: date,
    ) -> bool:
        passenger = PassengerRepository.get_by_id(passenger_id=passenger_id)
        if passenger:
            PassengerRepository.update(
                passenger=passenger,
                name=name,
                document=document,
                document_type=document_type,
                email=email,
                phone=phone,
                birth_date=birth_date,
            )

    @staticmethod
    def get_all() -> list[Passenger]:
        return PassengerRepository.get_all()

    @staticmethod
    def get_by_id(passenger_id: int) -> list[Passenger]:
        if passenger_id:
            return PassengerRepository.get_by_id(passenger_id=passenger_id)
        return ValueError("El Pasajero No Existe")

    @staticmethod
    def search_by_name(name: str) -> list[Passenger]:
        if name:
            return PassengerRepository.search_by_name(name=name)
        return ValueError("El Pasajero No Existe")
