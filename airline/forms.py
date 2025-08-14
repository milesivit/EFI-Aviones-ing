from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import DateTimeInput

from airline.models import Flight, FlightStatus, Passenger, Plane, Reservation
from airline.services.flight import FlightService

class PassengerForm(forms.Form):
    # Campo para el nombre del pasajero
    name = forms.CharField(
        label="Name",
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control"}),  # Se aplica clase de Bootstrap
    )

    # Campo para el documento de identidad
    document = forms.CharField(
        label="Document",
        max_length=50,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    # Tipo de documento (pasaporte, DNI, etc.)
    document_type = forms.ChoiceField(
        label="Document Type",
        choices=Passenger.DOCUMENT_TYPE_CHOICES,  # Se obtiene de los tipos definidos en el modelo
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    # Campo de correo electrónico
    email = forms.EmailField(
        label="Email", 
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )

    # Número de teléfono
    phone = forms.CharField(
        label="Phone",
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    # Fecha de nacimiento
    birth_date = forms.DateField(
        label="Birth Date",
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),  # Input tipo fecha
    )

    # Validación personalizada para la fecha de nacimiento
    def clean_birth_date(self):
        birth_date = self.cleaned_data.get("birth_date")
        # La fecha de nacimiento no puede estar en el futuro
        if birth_date and birth_date > date.today():
            raise ValidationError("Birth date cannot be in the future.")
        return birth_date

    # Constructor personalizado
    def __init__(self, *args, flight_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Guardamos el vuelo asociado para posibles validaciones adicionales
        self.flight_id = flight_id

class CreateFlightForm(forms.Form):
    # Campo para el aeropuerto o ciudad de origen
    origin = forms.CharField(
        max_length=150,
        label="Origen",
        widget=forms.TextInput(attrs={"class": "form-control"}),  # estilo Bootstrap
    )

    # Campo para el aeropuerto o ciudad de destino
    destination = forms.CharField(
        max_length=150,
        label="Destino",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    # Fecha y hora de salida del vuelo
    departure_date = forms.DateTimeField(
        label="Fecha y hora de salida",
        widget=DateTimeInput(
            attrs={"class": "form-control", "type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",  # formato HTML5 datetime-local
        ),
        input_formats=["%Y-%m-%dT%H:%M"],  # formato aceptado al validar
    )

    # Fecha y hora de llegada del vuelo
    arrival_date = forms.DateTimeField(
        label="Fecha y hora de llegada",
        widget=DateTimeInput(
            attrs={"class": "form-control", "type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M"],
    )

    # Estado del vuelo (activo, cancelado, retrasado, etc.)
    status_id = forms.ModelChoiceField(
        queryset=FlightStatus.objects.all(),  # Se llena con todos los estados
        label="Estado del Vuelo",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    # Precio base del boleto
    base_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="Precio base del boleto",
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )

    # Avión asignado al vuelo
    plane_id = forms.ModelChoiceField(
        queryset=Plane.objects.all(),
        label="Avion a asignar al vuelo",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    # Validación del precio base
    def clean_base_price(self):
        price = self.cleaned_data.get("base_price")
        if price is None:
            raise forms.ValidationError("Debes ingresar un precio base valido.")
        if price <= 0:
            raise forms.ValidationError("El precio base no puede ser 0 o menos.")
        return price

    # Validaciones globales del formulario
    def clean(self):
        cleaned_data = super().clean()
        departure = cleaned_data.get("departure_date")
        arrival = cleaned_data.get("arrival_date")
        plane = cleaned_data.get("plane_id")

        # Validar que la fecha de llegada sea posterior a la de salida
        if departure and arrival:
            if arrival <= departure:
                raise ValidationError(
                    "La fecha de llegada debe ser posterior a la de salida."
                )

        # Validar que el avión no tenga otro vuelo en ese rango horario
        if plane and departure and arrival:
            overlapping_flights = Flight.objects.filter(
                plane_id=plane, departure_date__lt=arrival, arrival_date__gt=departure
            )
            if overlapping_flights.exists():
                raise ValidationError(
                    "El avión seleccionado ya tiene otro vuelo asignado en ese rango horario."
                )

        return cleaned_data

    # Guardar los datos usando el servicio FlightService
    def save(self):
        origin = self.cleaned_data["origin"]
        destination = self.cleaned_data["destination"]
        departure_date = self.cleaned_data["departure_date"]
        arrival_date = self.cleaned_data["arrival_date"]
        status = self.cleaned_data["status_id"]
        base_price = (self.cleaned_data["base_price"],)  # atención: está como tupla
        plane = self.cleaned_data["plane_id"]

        # Crear el vuelo usando el servicio
        return FlightService.create(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            arrival_date=arrival_date,
            status_id=status.id,
            base_price=base_price,
            plane_id=plane.id,
        )

class UpdateFlightForm(forms.Form): 
    # Campo de texto para el origen del vuelo.
    origin = forms.CharField(
        max_length=150,
        label="Origen",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    
    # Campo de texto para el destino del vuelo.
    destination = forms.CharField(
        max_length=150,
        label="Destino",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    
    # Fecha y hora de salida del vuelo. Formateada para input de tipo datetime-local.
    departure_date = forms.DateTimeField(
        label="Fecha y hora de salida",
        widget=DateTimeInput(
            attrs={"class": "form-control", "type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M"],
    )
    
    # Fecha y hora de llegada del vuelo.
    arrival_date = forms.DateTimeField(
        label="Fecha y hora de llegada",
        widget=DateTimeInput(
            attrs={"class": "form-control", "type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M"],
    )
    
    # Selección de estado del vuelo desde la tabla FlightStatus.
    status_id = forms.ModelChoiceField(
        queryset=FlightStatus.objects.all(),
        label="Estado del Vuelo",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    
    # Precio base del boleto. Debe ser un número decimal positivo.
    base_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="Precio base del boleto",
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )
    
    # Selección de avión a asignar al vuelo desde la tabla Plane.
    plane_id = forms.ModelChoiceField(
        queryset=Plane.objects.all(),
        label="Avion a asignar al vuelo",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    # Validación individual del precio base.
    def clean_base_price(self):
        price = self.cleaned_data.get("base_price")
        if price is None:
            raise forms.ValidationError("Debes ingresar un precio base valido.")
        if price <= 0:
            raise forms.ValidationError("El precio base no puede ser 0 o menos.")
        return price

    # Constructor que recibe opcionalmente un flight_id para diferenciar actualización de creación.
    def __init__(self, *args, flight_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.flight_id = flight_id  # Guardamos el id del vuelo actual si es update.

    # Validación general de los datos del formulario.
    def clean(self):
        cleaned_data = super().clean()
        departure = cleaned_data.get("departure_date")
        arrival = cleaned_data.get("arrival_date")
        plane = cleaned_data.get("plane_id")

        # Validar que la llegada sea posterior a la salida.
        if departure and arrival:
            if arrival <= departure:
                raise ValidationError(
                    "La fecha de llegada debe ser posterior a la de salida."
                )

        # Validar que el avión no tenga vuelos que se solapen.
        if plane and departure and arrival:
            overlapping_flights = Flight.objects.filter(
                plane_id=plane, departure_date__lt=arrival, arrival_date__gt=departure
            )
            # Si es update, excluir el vuelo actual
            if self.flight_id:
                overlapping_flights = overlapping_flights.exclude(id=self.flight_id)

            if overlapping_flights.exists():
                raise ValidationError(
                    "El avión seleccionado ya tiene otro vuelo asignado en ese rango horario."
                )

        return cleaned_data

    # Método para actualizar el vuelo usando FlightService.
    def save(self):
        origin = self.cleaned_data["origin"]
        destination = self.cleaned_data["destination"]
        departure_date = self.cleaned_data["departure_date"]
        arrival_date = self.cleaned_data["arrival_date"]
        duration = self.cleaned_data["duration"]  # Nota: 'duration' no está definido en el formulario
        status = self.cleaned_data["status_id"]
        base_price = (self.cleaned_data["base_price"],)  # Nota: se crea como tupla innecesaria
        plane = self.cleaned_data["plane_id"]

        return FlightService.update(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            arrival_date=arrival_date,
            duration=duration,
            status_id=status.id,
            base_price=base_price,
            plane_id=plane.id,
        )

class CreatePlaneForm(forms.Form):
    
    # Campo de texto para el modelo del avión.
    model = forms.CharField(
        max_length=150,
        label="Modelo",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    
    # Campo numérico para la capacidad total del avión.
    capacity = forms.IntegerField(
        max_value=9999999,
        label="Capacidad total del avion",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    
    # Campo numérico para el número total de filas del avión.
    rows = forms.IntegerField(
        max_value=9999999,
        label="Filas totales del avion",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    
    # Campo numérico para el número total de columnas del avión.
    columns = forms.IntegerField(
        max_value=9999999,
        label="Columnas totales del avion",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    # Validación general de los datos del formulario.
    def clean(self):
        cleaned_data = super().clean()
        capacity = cleaned_data.get("capacity")
        rows = cleaned_data.get("rows")
        columns = cleaned_data.get("columns")

        # Verificar que todos los campos tengan valores ingresados.
        if capacity is None or rows is None or columns is None:
            raise ValidationError(
                "Debes ingresar un valor válido para capacidad, filas y columnas."
            )

        # Verificar que los valores sean mayores que cero.
        if capacity <= 0 or rows <= 0 or columns <= 0:
            raise ValidationError("Los valores ingresados no pueden ser 0 o menos.")

        return cleaned_data

class UpdatePlaneForm(forms.Form):
    # Campo de texto para el modelo del avión.
    model = forms.CharField(
        max_length=150,
        label="Modelo",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    
    # Campo numérico para la capacidad total del avión.
    capacity = forms.IntegerField(
        max_value=9999999,
        label="Capacidad total del avión",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    
    # Campo numérico para el número total de filas del avión.
    rows = forms.IntegerField(
        max_value=9999999,
        label="Filas totales del avión",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    
    # Campo numérico para el número total de columnas del avión.
    columns = forms.IntegerField(
        max_value=9999999,
        label="Columnas totales del avión",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    # Constructor personalizado para recibir opcionalmente el ID del avión a actualizar.
    def __init__(self, *args, **kwargs):
        # Capturamos plane_id y lo removemos de kwargs para no romper el __init__ de forms.Form
        self.plane_id = kwargs.pop("plane_id", None)
        super().__init__(*args, **kwargs)

    # Validación general de los datos del formulario.
    def clean(self):
        cleaned_data = super().clean()
        capacity = cleaned_data.get("capacity")
        rows = cleaned_data.get("rows")
        columns = cleaned_data.get("columns")

        # Verificar que todos los campos tengan valores ingresados.
        if capacity is None or rows is None or columns is None:
            raise ValidationError(
                "Debes ingresar un valor válido para capacidad, filas y columnas."
            )

        # Verificar que los valores sean mayores que cero.
        if capacity <= 0 or rows <= 0 or columns <= 0:
            raise ValidationError("Los valores ingresados no pueden ser 0 o menos.")

        return cleaned_data

