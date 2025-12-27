# domain/errors.py
class DomainError(Exception):
    """Базовое доменное исключение."""


class UserAlreadyExistsError(DomainError):
    """Пользователь с таким telegram_id уже существует."""


class UserNotFoundError(DomainError):
    """Пользователь не найден."""


class UserUpdateError(DomainError):
    """Ошибка при обновлении данных пользователя."""


class UserDeleteError(DomainError):
    """Ошибка при удалении пользователя."""
