from airline.models import (
    User,
    Plane,
    FlightStatus,
    Flight,
    Passenger,
    Seat,
    Reservation,
    Ticket,
)
from rest_framework import serializers

from airline.services.plane import PlaneService
from airline.services.flight_status import FlightStatusService
from airline.services.flight import FlightService
from airline.services.passenger import PassengerService
from airline.services.seat import SeatService
from airline.services.reservation import ReservationService
from airline.services.ticket import TicketService

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:  # la clase Meta indica a DRF que modelo usar para generar los campos
        model = User
        fields = [
            "id",
            "username",
            "email",
            "role",
            "is_active",
            "is_staff",
            "password",
        ]  # lista de campos que el serializer expondra

    def create(
        self, validated_data
    ):  # metodo que sobrescribís para controlar cómo crear una instancia de User cuando el serializer recibe datos validos
        password = validated_data.pop(
            "password", None
        )  # se extrae la clave de validated_data, pop devuelve el valor si existe; si no, devuelve None, evita que la contra quede en validated_data
        user = User.objects.create_user(
            password=password, **validated_data
        )  # usa el metodo de create_user para hacer todo el laburo
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)  # encripta correctamente la nueva contr

        instance.save()
        return instance


class PlaneSerializer(serializers.ModelSerializer):
    """
    Serializer del modelo Plane.
    Usa ModelSerializer para mantener compatibilidad con la UI de DRF,
    pero delega la lógica de negocio al PlaneService.
    """

    class Meta:
        model = Plane
        fields = ["id", "model", "capacity", "rows", "columns"]

    def create(self, validated_data):
        """
        Crea un nuevo avión usando la capa de servicio.
        """
        plane = PlaneService.create(
            model=validated_data["model"],
            capacity=validated_data["capacity"],
            rows=validated_data["rows"],
            columns=validated_data["columns"],
        )
        return plane

    def update(self, instance, validated_data):
        """
        Actualiza un avión existente usando la capa de servicio.
        """
        plane = PlaneService.update(
            plane_id=instance.id,
            model=validated_data.get("model", instance.model),
            capacity=validated_data.get("capacity", instance.capacity),
            rows=validated_data.get("rows", instance.rows),
            columns=validated_data.get("columns", instance.columns),
        )
        return plane

class FlightStatusSerializer(serializers.ModelSerializer):
    """
    Serializer para FlightStatus.
    Usa ModelSerializer (para mantener la compatibilidad con la UI de DRF),
    pero toda la lógica de creación/actualización se delega a FlightStatusService.
    """

    class Meta:
        model = FlightStatus
        fields = ["id", "status"]

    def create(self, validated_data):
        """
        Crea un nuevo estado de vuelo usando la capa de servicio.
        """
        return FlightStatusService.create(status=validated_data["status"])

    def update(self, instance, validated_data):
        """
        Actualiza un estado de vuelo existente usando la capa de servicio.
        """
        return FlightStatusService.update(
            flight_status=instance,
            status=validated_data.get("status", instance.status),
        )


class FlightSerializer(serializers.ModelSerializer):
    """
    Serializer para Flight.
    Usa ModelSerializer solo por compatibilidad con la UI de DRF,
    pero delega toda la lógica de negocio a FlightService.
    """

    # Campos de entrada (para POST/PUT)
    status = serializers.PrimaryKeyRelatedField(
        queryset=FlightStatus.objects.all(), write_only=True
    )
    plane = serializers.PrimaryKeyRelatedField(
        queryset=Plane.objects.all(), write_only=True
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, write_only=True
    )

    # Campos de salida (para GET)
    status_display = serializers.StringRelatedField(source="status", read_only=True)
    plane_display = serializers.StringRelatedField(source="plane", read_only=True)
    user_display = serializers.StringRelatedField(source="user", many=True, read_only=True)

    class Meta:
        model = Flight
        fields = [
            "id",
            "origin",
            "destination",
            "departure_date",
            "arrival_date",
            "duration",
            "base_price",
            "status",
            "plane",
            "user",
            "status_display",
            "plane_display",
            "user_display",
        ]

    def create(self, validated_data):
        """
        Crea un nuevo vuelo usando la capa de servicio.
        """
        status = validated_data["status"]
        plane = validated_data["plane"]
        users = validated_data["user"]

        flight = FlightService.create(
            origin=validated_data["origin"],
            destination=validated_data["destination"],
            departure_date=validated_data["departure_date"],
            arrival_date=validated_data["arrival_date"],
            duration=validated_data["duration"],
            status=status.id,
            base_price=validated_data["base_price"],
            plane_id=plane.id,
            user_id=[u.id for u in users],
        )
        return flight

    def update(self, instance, validated_data):
        """
        Actualiza un vuelo existente usando la capa de servicio.
        """
        status = validated_data.get("status", instance.status)
        plane = validated_data.get("plane", instance.plane)
        users = validated_data.get("user", instance.user.all())

        flight = FlightService.update(
            flight=instance,
            origin=validated_data.get("origin", instance.origin),
            destination=validated_data.get("destination", instance.destination),
            departure_date=validated_data.get("departure_date", instance.departure_date),
            arrival_date=validated_data.get("arrival_date", instance.arrival_date),
            duration=validated_data.get("duration", instance.duration),
            status=status.id,
            base_price=validated_data.get("base_price", instance.base_price),
            plane_id=plane.id,
            user_ids=[u.id for u in users],
        )
        return flight


class PassengerSerializer(serializers.ModelSerializer):
    """
    Serializer del modelo Passenger.
    Usa ModelSerializer solo por compatibilidad con la UI de DRF,
    pero delega toda la lógica de creación y actualización al PassengerService.
    """

    class Meta:
        model = Passenger
        fields = [
            "id",
            "name",
            "document",
            "document_type",
            "email",
            "phone",
            "birth_date",
        ]

    def create(self, validated_data):
        """
        Crea un nuevo pasajero usando la capa de servicio.
        """
        return PassengerService.create(
            name=validated_data["name"],
            document=validated_data["document"],
            document_type=validated_data["document_type"],
            email=validated_data["email"],
            phone=validated_data["phone"],
            birth_date=validated_data["birth_date"],
        )

    def update(self, instance, validated_data):
        """
        Actualiza un pasajero existente usando la capa de servicio.
        """
        return PassengerService.update(
            passenger_id=instance.id,
            name=validated_data.get("name", instance.name),
            document=validated_data.get("document", instance.document),
            document_type=validated_data.get("document_type", instance.document_type),
            email=validated_data.get("email", instance.email),
            phone=validated_data.get("phone", instance.phone),
            birth_date=validated_data.get("birth_date", instance.birth_date),
        )


class SeatSerializer(serializers.ModelSerializer):
    """
    Serializer del modelo Seat.
    Usa ModelSerializer para mantener compatibilidad con la UI de DRF,
    pero delega toda la lógica de negocio a SeatService.
    """

    # Para POST/PUT -> se pasa solo el id del avión
    plane = serializers.PrimaryKeyRelatedField(
        queryset=Plane.objects.all(), write_only=True
    )

    # Para GET -> se muestra el avión relacionado
    plane_display = serializers.StringRelatedField(source="plane", read_only=True)

    class Meta:
        model = Seat
        fields = [
            "id",
            "number",
            "row",
            "column",
            "seat_type",
            "status",
            "plane",
            "plane_display",
        ]

    def create(self, validated_data):
        """
        Crea un asiento nuevo usando la capa de servicio.
        """
        return SeatService.create(
            number=validated_data["number"],
            row=validated_data["row"],
            column=validated_data["column"],
            seat_type=validated_data["seat_type"],
            status=validated_data["status"],
            plane_id=validated_data["plane"].id,
        )

    def update(self, instance, validated_data):
        """
        Actualiza un asiento existente usando la capa de servicio.
        """
        return SeatService.update(
            seat_id=instance.id,
            number=validated_data.get("number", instance.number),
            row=validated_data.get("row", instance.row),
            column=validated_data.get("column", instance.column),
            seat_type=validated_data.get("seat_type", instance.seat_type),
            status=validated_data.get("status", instance.status),
            plane_id=validated_data.get("plane", instance.plane).id,
        )


class ReservationSerializer(serializers.ModelSerializer):
    """
    Serializer del modelo Reservation.
    Usa ModelSerializer por compatibilidad con DRF,
    pero delega la creación y actualización al ReservationService.
    """

    # Para POST/PUT -> se envía solo el id de las relaciones
    flight = serializers.PrimaryKeyRelatedField(
        queryset=Flight.objects.all(), write_only=True
    )
    passenger = serializers.PrimaryKeyRelatedField(
        queryset=Passenger.objects.all(), write_only=True
    )
    seat = serializers.PrimaryKeyRelatedField(
        queryset=Seat.objects.all(), write_only=True
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True
    )

    # Para GET -> se muestra la información completa
    flight_display = serializers.StringRelatedField(source="flight", read_only=True)
    passenger_display = serializers.StringRelatedField(source="passenger", read_only=True)
    seat_display = serializers.StringRelatedField(source="seat", read_only=True)
    user_display = serializers.StringRelatedField(source="user", read_only=True)

    class Meta:
        model = Reservation
        fields = [
            "id",
            "status",
            "reservation_date",
            "price",
            "reservation_code",
            "flight",
            "flight_display",
            "passenger",
            "passenger_display",
            "seat",
            "seat_display",
            "user",
            "user_display",
        ]

    def create(self, validated_data):
        """
        Crea una nueva reserva usando la capa de servicio.
        """
        return ReservationService.create(
            status=validated_data["status"],
            reservation_date=validated_data["reservation_date"],
            price=validated_data["price"],
            reservation_code=validated_data["reservation_code"],
            flight_id=validated_data["flight"].id,
            passenger_id=validated_data["passenger"].id,
            seat_id=validated_data["seat"].id,
            user_id=validated_data["user"].id,
        )

    def update(self, instance, validated_data):
        """
        Actualiza una reserva existente usando la capa de servicio.
        """
        return ReservationService.update(
            reservation_id=instance.id,
            status=validated_data.get("status", instance.status),
            reservation_date=validated_data.get("reservation_date", instance.reservation_date),
            price=validated_data.get("price", instance.price),
            reservation_code=validated_data.get("reservation_code", instance.reservation_code),
            flight_id=validated_data.get("flight", instance.flight).id,
            passenger_id=validated_data.get("passenger", instance.passenger).id,
            seat_id=validated_data.get("seat", instance.seat).id,
            user_id=validated_data.get("user", instance.user).id,
        )

class TicketSerializer(serializers.ModelSerializer):
    """
    Serializer del modelo Ticket.
    Usa ModelSerializer para mantener compatibilidad con la UI de DRF,
    pero delega toda la lógica de creación y actualización al TicketService.
    """

    # Para POST/PUT -> solo se envía el id de la reserva
    reservation = serializers.PrimaryKeyRelatedField(
        queryset=Reservation.objects.all(), write_only=True
    )

    # Para GET -> se muestra la información expandida
    reservation_display = serializers.StringRelatedField(source="reservation", read_only=True)

    class Meta:
        model = Ticket
        fields = [
            "id",
            "barcode",
            "issue_date",
            "status",
            "reservation",
            "reservation_display",
        ]

    def create(self, validated_data):
        """
        Crea un nuevo ticket usando la capa de servicio.
        """
        return TicketService.create(
            barcode=validated_data["barcode"],
            issue_date=validated_data["issue_date"],
            status=validated_data["status"],
            reservation_id=validated_data["reservation"].id,
        )

    def update(self, instance, validated_data):
        """
        Actualiza un ticket existente usando la capa de servicio.
        """
        return TicketService.update(
            ticket_id=instance.id,
            barcode=validated_data.get("barcode", instance.barcode),
            issue_date=validated_data.get("issue_date", instance.issue_date),
            status=validated_data.get("status", instance.status),
            reservation_id=validated_data.get("reservation", instance.reservation).id,
        )