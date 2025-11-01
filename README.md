# Sistema de Gestión de Aerolínea ✈️

## 🚀 Instrucciones rápidas de instalación

A continuación tienes los comandos listos para copiar y pegar para clonar el repositorio, instalar dependencias, aplicar migraciones y crear un superusuario.

## 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/milesivit/EFI-Aviones-ing.git
cd EFI-Aviones-ing
```
## 2️⃣ Crear y activar un entorno virtual
```bash
python -m venv env
source env/bin/activate   # En Linux/Mac
env\Scripts\activate      # En Windows
```
## 3️⃣ Instalar requerimientos
```bash
pip install -r requirements.txt
```
## 4️⃣ Aplicar migraciones
```bash
python manage.py migrate
```
## 5️⃣ Crear un superusuario
```bash
python manage.py createsuperuser
```
## 6️⃣ Json para datos en la DB
```bash
 python manage.py loaddata airline/fixtures/initial_data.json
```
## 7️⃣ Levantar el servidor
```bash
python manage.py runserver
```
## 📋 Información del Proyecto

Este proyecto fue desarrollado como un **prototipo para un sistema de gestión de aerolíneas**

## 🛠️ Flujo de trabajo en el Backend

El backend fue desarrollado con **Django**, siguiendo una arquitectura **modular y organizada**.  
Se implementó el flujo completo, incluyendo:

- **Model**: Definición de la estructura de la base de datos.
- **Repository**: Encapsula la lógica de acceso a datos.
- **Service**: Implementación de la lógica de negocio y reglas de la aplicación.
- **View**: Manejo de las solicitudes HTTP y generación de respuestas.
- **URL**: Configuración de rutas para conectar vistas con endpoints.

Esta separación de responsabilidades permite **código más limpio, mantenible y escalable**.

---

## 🗄️ Modelos de Datos y Relaciones

El sistema incluye los modelos clave para una aplicación de aerolíneas:

- **Plane**: Representa las aeronaves (modelo, capacidad, filas y columnas).
- **User**: Usuarios del sistema (admin, vendedores) con credenciales y roles.
- **Flight**: Vuelos con origen, destino, horarios, precio base, vinculados a un avión y usuarios.
- **Passenger**: Datos personales de quienes reservan vuelos.
- **Seat**: Asientos específicos del avión (fila, columna, tipo y estado).
- **Reservation**: Reservas de pasajeros vinculadas a vuelo, asiento y pasajero, con un código único.
- **Ticket**: Tickets emitidos para una reserva, con código de barras y fecha de emisión.

Las relaciones están construidas principalmente con **ForeignKey** y **OneToOne**, asegurando integridad de datos y consultas eficientes.

---

## 💻 Tecnologías Utilizadas
- **Django** (Backend)
- **Bootstrap 4** (Estilos y UI)
- **HTML5** (Estructura)
- **CSS3** (Estilos personalizados)

---

## 👨‍💻 Desarrolladores
- **Milena Sivit**
- **Santiago Baez**

---
