# domain/errors.py
class DomainError(Exception):
    """Базовое доменное исключение."""


class EntityAlreadyExistsError(DomainError):
    """Пользователь с таким telegram_id уже существует."""


class EntityNotFoundError(DomainError):
    """Пользователь не найден."""


class EntityUpdateError(DomainError):
    """Ошибка при обновлении данных пользователя."""


class EntityDeleteError(DomainError):
    """Ошибка при удалении пользователя."""