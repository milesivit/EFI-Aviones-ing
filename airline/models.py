from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager 
# Create your models here.
from django.db import models

class Plane(models.Model): #clase avion
    model = models.CharField(max_length=100) #modelo
    capacity = models.PositiveIntegerField() #capacidad. el positive adelante sirve para que no hayan valores negativos, ya que capacidad, fila y columna no tendria que ser negativo
    rows = models.PositiveIntegerField() #filas
    columns = models.PositiveIntegerField() #columnas

    def __str__(self):
        return f"{self.model} - Capacity: {self.capacity}"


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, role='user'):
        if not username:
            raise ValueError('El usuario debe tener username')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, role=role)
        user.set_password(password)  # hashea y guarda la contraseña
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(username, email, password, role='admin')
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def __str__(self):
        return self.username
    
class FlightStatus(models.Model):
    status = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.status}"
    
class Flight(models.Model): #clase vuelo
    origin = models.CharField(max_length=100) #origen
    destination = models.CharField(max_length=100)
    departure_date = models.DateTimeField() #fecha salida
    arrival_date = models.DateTimeField() #fecha llegada
    duration = models.DurationField() #duracion, durationfield permite calcular facilmente diferencias entre fechas
    base_price = models.DecimalField(max_digits=10, decimal_places=2) #precio base

    status = models.ForeignKey(FlightStatus, on_delete=models.CASCADE) #estado id
    plane = models.ForeignKey(Plane, on_delete=models.CASCADE) #avion id
    user = models.ManyToManyField(User)

    def __str__(self):
        return f"{self.origin} → {self.destination} ({self.departure_date.date()})"
    

class Passenger(models.Model):
    PASSPORT = 'passport'
    DNI = 'dni'
    ID_CARD = 'id_card'
    DOCUMENT_TYPE_CHOICES = [
        (PASSPORT, 'Passport'),
        (DNI, 'DNI'),
        (ID_CARD, 'ID Card'),
    ]
    name = models.CharField(max_length=255) #nombre
    document = models.CharField(max_length=50) #documento
    document_type = models.CharField(max_length=50) #tipo de documento
    email = models.EmailField() 
    phone = models.CharField(max_length=20) #telefono
    birth_date = models.DateField() #fecha de nacimiento

    def __str__(self):
        return f"{self.name} ({self.document})"

class Seat(models.Model):
    number = models.CharField(max_length=10)  #numero de butakera
    row = models.PositiveIntegerField() #fila
    column = models.CharField(max_length=1)  #columna, ej: A, B, etc
    seat_type = models.CharField(max_length=50)  #tipo de asiento, ej: "economico", "business"
    status = models.CharField(max_length=50)     #estadp ej: "disponible", "ocupado"

    plane = models.ForeignKey(Plane, on_delete=models.CASCADE) #avion id
    
    def __str__(self):
        return f"{self.row}{self.column} (Plane ID: {self.plane.id})"


class Reservation(models.Model):
    status = models.CharField(max_length=50) #estado
    reservation_date = models.DateTimeField() #fecha de reserva 
    price = models.DecimalField(max_digits=10, decimal_places=2) #precio
    reservation_code = models.CharField(max_length=20, unique=True) #codigo de reserva, unique=True permite que no haya otro codigo igual

    flight = models.ForeignKey(Flight, on_delete=models.CASCADE) #vuelo id
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE) #pasajero id
    seat = models.OneToOneField(Seat, on_delete=models.CASCADE) #asiento id
    user = models.ForeignKey(User, on_delete=models.CASCADE) #usuario id
    
    def __str__(self):
        return f"Reservation {self.reservation_code} for {self.passenger.name}"


class Ticket(models.Model):
    barcode = models.CharField(max_length=100, unique=True) #codigo de barra, muy ferretera eso
    issue_date = models.DateTimeField(auto_now_add=True) #fecha de emision
    status = models.CharField(max_length=50)  # estado, ej: "activo", "usado", "cancelado"

    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE) #reserva id
    
    def __str__(self):
        return f"Ticket {self.barcode} - {self.status}"
    