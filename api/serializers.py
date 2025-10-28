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


class PlaneSerializer(
    serializers.ModelSerializer
):  # modelserializer ya te hace el create y el update por detras
    class Meta:  # al no necesitar logica personalizada se puede poner asi de lleno, no es como usuario
        model = Plane
        fields = [
            "id",
            "model",
            "capacity",
            "rows",
            "columns",
        ]  # lista de campos que el serializer expondra


class FlightStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlightStatus
        fields = ["id", "status"]  # lista de campos que el serializer expondra


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


class PassengerSerializer(
    serializers.ModelSerializer
):  # modelserializer ya te hace el create y el update por detras
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
        ]  # lista de campos que el serializer expondra


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
