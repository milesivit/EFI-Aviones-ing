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
from airline.services.passenger import PassengerService

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


class PlaneSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    model = serializers.CharField(max_length=100)
    capacity = serializers.IntegerField()
    rows = serializers.IntegerField()
    columns = serializers.IntegerField()

    def create(self, validated_data) -> "Plane":
        """
        crea un nuevo avion usando PlaneService
        """
        return PlaneService.create(
            model=validated_data["model"],
            capacity=validated_data["capacity"],
            rows=validated_data["rows"],
            columns=validated_data["columns"],
        )

    def update(self, instance: "Plane", validated_data) -> "Plane":
        """
        actualiza un avion existente usando PlaneService
        """
        PlaneService.update(
            plane_id=instance.id,
            model=validated_data.get("model", instance.model),
            capacity=validated_data.get("capacity", instance.capacity),
            rows=validated_data.get("rows", instance.rows),
            columns=validated_data.get("columns", instance.columns),
        )
        #devuelve el objeto actualizado
        return PlaneService.get_by_id(instance.id)

class FlightStatusSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    status = serializers.CharField(max_length=50)

    def create(self, validated_data) -> "FlightStatus": #forward reference, y no necesita importar el modelo.
        """
        crea un estado de vuelo usando FlightStatusService
        """
        return FlightStatusService.create(status=validated_data["status"])

    def update(self, instance: "FlightStatus", validated_data) -> "FlightStatus":
        """
        actualiza un estado de vuelo existente usando FlightStatusService
        """
        return FlightStatusService.update(
            flight_status=instance,
            status=validated_data.get("status", instance.status),
        )


class FlightSerializer(serializers.ModelSerializer):
    # para (POST/PUT) es decir que cuando hagas uno de esto se manda el id de lleno
    status = serializers.PrimaryKeyRelatedField(
        queryset=FlightStatus.objects.all(), write_only=True
    )
    plane = serializers.PrimaryKeyRelatedField(
        queryset=Plane.objects.all(), write_only=True
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, write_only=True
    )

    # para (GET) aca te llega la data
    status_display = serializers.StringRelatedField(source="status", read_only=True)
    plane_display = serializers.StringRelatedField(source="plane", read_only=True)
    user_display = serializers.StringRelatedField(
        source="user", many=True, read_only=True
    )

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


class PassengerSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    document = serializers.CharField(max_length=50)
    document_type = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=50)
    birth_date = serializers.DateField()

    def create(self, validated_data) -> "Passenger":
        """
        Crea un pasajero con service
        """
        return PassengerService.create(
            name=validated_data["name"],
            document=validated_data["document"],
            document_type=validated_data["document_type"],
            email=validated_data["email"],
            phone=validated_data["phone"],
            birth_date=validated_data["birth_date"],
        )

    def update(self, instance: "Passenger", validated_data) -> "Passenger":
        """
        actualiza un pasajero
        """
        return PassengerService.update(
            passenger=instance,
            name=validated_data.get("name", instance.name),
            document=validated_data.get("document", instance.document),
            document_type=validated_data.get("document_type", instance.document_type),
            email=validated_data.get("email", instance.email),
            phone=validated_data.get("phone", instance.phone),
            birth_date=validated_data.get("birth_date", instance.birth_date),
        )



class SeatSerializer(serializers.ModelSerializer):
    # para (POST/PUT) es decir que cuando hagas uno de esto se manda el id de lleno
    plane = serializers.PrimaryKeyRelatedField(
        queryset=Plane.objects.all(), write_only=True
    )

    # para (GET) aca te llega la data
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
        ]  # lista de campos que el serializer expondra


class ReservationSerializer(serializers.ModelSerializer):
    # para (POST/PUT) es decir que cuando hagas uno de esto se manda el id de lleno
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

    # para (GET) aca te llega la data
    flight_display = serializers.StringRelatedField(source="flight", read_only=True)
    passenger_display = serializers.StringRelatedField(
        source="passenger", read_only=True
    )
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


class TicketSerializer(serializers.ModelSerializer):
    # para (POST/PUT) es decir que cuando hagas uno de esto se manda el id de lleno
    reservation = serializers.PrimaryKeyRelatedField(
        queryset=Reservation.objects.all(), write_only=True
    )

    # para (GET) aca te llega la data
    reservation_display = serializers.StringRelatedField(
        source="reservation", read_only=True
    )

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
