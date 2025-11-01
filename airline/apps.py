from django.apps import (
    AppConfig,
)  # Importa AppConfig, la clase base para configurar aplicaciones en Django


class AirlineConfig(AppConfig):
    # Configuración de la app 'airline' dentro del proyecto Django

    default_auto_field = "django.db.models.BigAutoField"
    # Define el tipo de campo por defecto para los IDs de los modelos de esta app.
    # BigAutoField es un entero grande que se incrementa automáticamente para cada registro.

    name = "airline"
    # Nombre de la aplicación. Django lo usa para registrar la app y asociarla con sus modelos, vistas y demás componentes.
