from django.contrib.auth.hashers import make_password
from airline.models import User #esta bien el modelo aca ya que El Service solo recibe o devuelve objetos y llama al Repository para hacer el trabajo real.
from airline.repositories.user import UserRepository


class UserService:

    @staticmethod
    def create(username: str, password: str, email: str, role: str) -> User:
        user = UserRepository.create(
            username=username, password=password, email=email, role=role
        )

        if role == "admin":
            # Llamamos a un nuevo método del Repository para guardar el cambio
            # Nota: Podrías usar el método 'update' existente si lo adaptas,
            # o crear uno específico para este tipo de lógica.
            return UserRepository.update_staff_status(user=user, is_staff=True)

        return user

    @staticmethod
    def delete(user_id: int) -> bool:
        user = UserRepository.get_by_id(user_id=user_id)
        if user:
            return UserRepository.delete(user=user)
        return False

    @staticmethod
    def update(
        user_id: int,
        username: str,
        password: str,
        email: str,
        role: str,
    ) -> bool:
        user = UserRepository.get_by_id(user_id=user_id)
        if user:
            return UserRepository.update(
                user=user, username=username, password=password, email=email, role=role
            )
        return False

    @staticmethod
    def get_all() -> list[User]:
        return UserRepository.get_all()

    @staticmethod
    def get_by_id(user_id: int) -> User:
        if user_id:
            return UserRepository.get_by_id(user_id=user_id)
        return ValueError("El Usuario No Existe")

    @staticmethod
    def search_by_username(username: str) -> list[User]:
        if username:
            return UserRepository.search_by_username(username=username)
        return ValueError("El Usuario No Existe")
