from datetime import timedelta
from django import forms
from django.forms.widgets import DateTimeInput
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from airline.models import Flight, FlightStatus, Plane
from airline.services.flight import FlightService

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

        if departure and arrival:
            if arrival <= departure:
                raise forms.ValidationError("La fecha y hora de llegada debe ser posterior a la de salida.")
        
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
    
    def clean(self):
        cleaned_data = super().clean()
        departure = cleaned_data.get("departure_date")
        arrival = cleaned_data.get("arrival_date")

        if departure and arrival:
            if arrival <= departure:
                raise forms.ValidationError("La fecha y hora de llegada debe ser posterior a la de salida.")
        
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

