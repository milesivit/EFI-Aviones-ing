from datetime import timedelta
from django import forms
from django.forms.widgets import DateTimeInput
from django.core.exceptions import ValidationError
from datetime import date
from django.contrib.auth import authenticate
from airline.models import Flight, FlightStatus, Plane, Passenger, Reservation
from airline.services.flight import FlightService

class PassengerForm(forms.Form):
    name = forms.CharField(
        label="Name",
        max_length=255,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    document = forms.CharField(
        label="Document",
        max_length=50,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    document_type = forms.ChoiceField(
        label="Document Type",
        choices=Passenger.DOCUMENT_TYPE_CHOICES, 
        widget=forms.Select(
            attrs={'class': 'form-control'}
        )
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={'class': 'form-control'}
        )
    )
    phone = forms.CharField(
        label="Phone",
        max_length=20,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    birth_date = forms.DateField(
        label="Birth Date",
        widget=forms.DateInput(
            attrs={'class': 'form-control', 'type': 'date'}
        )
    )

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date and birth_date > date.today():
            raise ValidationError("Birth date cannot be in the future.")
        return birth_date
    
    def __init__(self, *args, flight_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.flight_id = flight_id  # guardo el vuelo para validar

    def clean_document(self):
        document = self.cleaned_data.get('document')
        if document and Passenger.objects.filter(document=document).exists():
            raise ValidationError("Ya existe un pasajero registrado con este documento.")
        return document

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Passenger.objects.filter(email=email).exists():
            raise ValidationError("Ya existe un pasajero registrado con este email.")
        return email
    
class CreateFlightForm(forms.Form):
    origin = forms.CharField(
        max_length=150,
        label="Origen",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    destination = forms.CharField(
        max_length=150,
        label="Destino",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    departure_date = forms.DateTimeField(
            label="Fecha y hora de salida",
            widget=DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local',
                },
                format='%Y-%m-%dT%H:%M'
            ),
            input_formats=['%Y-%m-%dT%H:%M']
        )
    arrival_date = forms.DateTimeField(
        label="Fecha y hora de llegada",
        widget=DateTimeInput(
            attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            },
            format='%Y-%m-%dT%H:%M'
        ),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    status_id = forms.ModelChoiceField(
        queryset = FlightStatus.objects.all(),
        label="Estado del Vuelo",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    base_price = forms.DecimalField(
        max_digits=10, 
        decimal_places=2,
        label="Precio base del boleto",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    plane_id = forms.ModelChoiceField(
        queryset = Plane.objects.all(),
        label="Avion a asignar al vuelo",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def clean_base_price(self):
        price = self.cleaned_data.get('base_price')
        
        if price is None:
            raise forms.ValidationError("Debes ingresar un precio base valido.")
    
        if price <= 0:
            raise forms.ValidationError("El precio base no puede ser 0 o menos.")
        
        return price

    def clean(self):
        cleaned_data = super().clean()
        departure = cleaned_data.get("departure_date")
        arrival = cleaned_data.get("arrival_date")
        plane = cleaned_data.get("plane_id")

        if departure and arrival:
            if arrival <= departure:
                raise ValidationError("La fecha de llegada debe ser posterior a la de salida.")

        # Validar solapamiento de vuelos con el mismo avión (sin excluir ningún id porque es creación)
        if plane and departure and arrival:
            overlapping_flights = Flight.objects.filter(
                plane_id=plane,
                departure_date__lt=arrival,
                arrival_date__gt=departure
            )
            if overlapping_flights.exists():
                raise ValidationError("El avión seleccionado ya tiene otro vuelo asignado en ese rango horario.")

        return cleaned_data

    def save(self):
        origin = self.cleaned_data['origin']
        destination = self.cleaned_data['destination']
        departure_date = self.cleaned_data['departure_date']
        arrival_date = self.cleaned_data['arrival_date']
        status = self.cleaned_data['status_id']
        base_price=self.cleaned_data['base_price'],
        plane = self.cleaned_data['plane_id']

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
    origin = forms.CharField(
        max_length=150,
        label="Origen",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    destination = forms.CharField(
        max_length=150,
        label="Destino",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    departure_date = forms.DateTimeField(
            label="Fecha y hora de salida",
            widget=DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local',
                },
                format='%Y-%m-%dT%H:%M'
            ),
            input_formats=['%Y-%m-%dT%H:%M']
    )
    arrival_date = forms.DateTimeField(
        label="Fecha y hora de llegada",
        widget=DateTimeInput(
            attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            },
            format='%Y-%m-%dT%H:%M'
        ),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    status_id = forms.ModelChoiceField(
        queryset = FlightStatus.objects.all(),
        label="Estado del Vuelo",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    base_price = forms.DecimalField(
        max_digits=10, 
        decimal_places=2,
        label="Precio base del boleto",        
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    plane_id = forms.ModelChoiceField(
        queryset = Plane.objects.all(),
        label="Avion a asignar al vuelo",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
        
    def clean_base_price(self):
        price = self.cleaned_data.get('base_price')
        
        if price is None:
            raise forms.ValidationError("Debes ingresar un precio base valido.")
    
        if price <= 0:
            raise forms.ValidationError("El precio base no puede ser 0 o menos.")
        
        return price
    
    def __init__(self, *args, flight_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.flight_id = flight_id  # <-- guardamos el id

    def clean(self):
        cleaned_data = super().clean()
        departure = cleaned_data.get("departure_date")
        arrival = cleaned_data.get("arrival_date")
        plane = cleaned_data.get("plane_id")

        if departure and arrival:
            if arrival <= departure:
                raise ValidationError("La fecha de llegada debe ser posterior a la de salida.")

        if plane and departure and arrival:
            overlapping_flights = Flight.objects.filter(
                plane_id=plane,
                departure_date__lt=arrival,
                arrival_date__gt=departure
            )
            # Si es update, excluir el vuelo actual
            if self.flight_id:
                overlapping_flights = overlapping_flights.exclude(id=self.flight_id)

            if overlapping_flights.exists():
                raise ValidationError("El avión seleccionado ya tiene otro vuelo asignado en ese rango horario.")

        return cleaned_data

    def save(self):
        origin = self.cleaned_data['origin']
        destination = self.cleaned_data['destination']
        departure_date = self.cleaned_data['departure_date']
        arrival_date = self.cleaned_data['arrival_date']
        duration = self.cleaned_data['duration']
        status = self.cleaned_data['status_id']
        base_price = self.cleaned_data['base_price'],
        plane = self.cleaned_data['plane_id']

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
    model = forms.CharField(
        max_length=150,
        label="Modelo",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    capacity = forms.IntegerField(
        max_value=9999999, 
        label="Capacidad total del avion",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    rows = forms.IntegerField(
        max_value=9999999, 
        label="Filas totales del avion",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    columns = forms.IntegerField(
        max_value=9999999, 
        label="Columnas totales del avion",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        capacity = cleaned_data.get("capacity")
        rows = cleaned_data.get("rows")
        columns = cleaned_data.get("columns")

        if capacity is None or rows is None or columns is None:
            raise ValidationError("Debes ingresar un valor válido para capacidad, filas y columnas.")

        if capacity <= 0 or rows <= 0 or columns <= 0:
            raise ValidationError("Los valores ingresados no pueden ser 0 o menos.")

        return cleaned_data

class UpdatePlaneForm(forms.Form):
    model = forms.CharField(
        max_length=150,
        label="Modelo",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    capacity = forms.IntegerField(
        max_value=9999999, 
        label="Capacidad total del avión",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    rows = forms.IntegerField(
        max_value=9999999, 
        label="Filas totales del avión",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    columns = forms.IntegerField(
        max_value=9999999, 
        label="Columnas totales del avión",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        # Capturamos plane_id y lo removemos de kwargs para no romper __init__ de forms.Form
        self.plane_id = kwargs.pop('plane_id', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        capacity = cleaned_data.get("capacity")
        rows = cleaned_data.get("rows")
        columns = cleaned_data.get("columns")

        if capacity is None or rows is None or columns is None:
            raise ValidationError("Debes ingresar un valor válido para capacidad, filas y columnas.")

        if capacity <= 0 or rows <= 0 or columns <= 0:
            raise ValidationError("Los valores ingresados no pueden ser 0 o menos.")

        return cleaned_data