from airline.models import User


class UserRepository:
    """
    Clase de repositorio que se encargará de conectarse con la base de datos
    para manipular usuarios.
    """

    @staticmethod
    def create(
        username: str,
        password: str,
        email: str,
        role: str,
    ) -> User:
        """
        Crea un nuevo usuario.

        Args:
            username: Nombre de usuario.
            password: Contraseña.
            email: Correo electrónico.
            role: Rol del usuario.

        Returns:
            Instancia del usuario creado.
        """
        return User.objects.create_user(
            username=username,
            password=password,
            email=email,
            role=role,
        )

    @staticmethod
    def delete(user: User) -> bool:
        """
        Elimina un usuario.

        Args:
            user: Instancia del usuario a eliminar.

        Returns:
            True si se elimina correctamente.

        Raises:
            ValueError: Si el usuario no existe.
        """
        try:
            user.delete()
            return True
        except User.DoesNotExist:
            raise ValueError("El usuario no existe")

    @staticmethod
    def update(user: User, username: str, password: str, email: str, role: str) -> User:
        user.username = username
        if password:  # <-- solo actualizo si password tiene contenido
            user.set_password(password)
        user.email = email
        user.role = role
        user.save()

        return user

    @staticmethod
    def get_all() -> list[User]:
        """
        Obtiene todos los usuarios registrados.

        Returns:
            Lista de usuarios.
        """
        return User.objects.all()

    @staticmethod
    def get_by_id(user_id: int) -> User | None:
        """
        Obtiene un usuario por su ID.

        Args:
            user_id: ID del usuario.

        Returns:
            Instancia del usuario o None si no existe.
        """
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @staticmethod
    def search_by_username(username: str) -> list[User]:
        """
        Busca usuarios cuyo nombre de usuario contenga el texto ingresado.

        Args:
            username: Texto parcial del nombre de usuario.

        Returns:
            Lista de usuarios coincidentes.
        """
        return User.objects.filter(username__icontains=username)

    @staticmethod
    def update_staff_status(user: User, is_staff: bool) -> User:
        """Actualiza solo el campo is_staff y lo guarda en la DB."""
        user.is_staff = is_staff
        user.save()  # <--- El .save() SÓLO va aquí
        return user
