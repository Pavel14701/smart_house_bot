import types
from typing import Any, Optional, Protocol, Self, Type  # type: ignore [attr-defined]
from uuid import UUID

from domain.entities import (
    AudioFileEntity,
    HomeEntity,
    HomeUserRoleEntity,
    SmartDeviceEntity,
    TelegramUserEntity,
    TextEventEntity,
)


class UUIDGenerator(Protocol):
    def __call__(self) -> UUID:
        ...


class MessageCacheProtocol(Protocol):
    async def save_message(
        self,
        message: TextEventEntity | AudioFileEntity,
        *,
        ttl: int | None = None,
    ) -> None:
        ...


class SessionProtocol(Protocol):
    
    async def commit(self) -> None:
        ...
    
    async def flush(self) -> None:
        ...
    
    async def rollback(self) -> None:
        ...
    
    async def begin(self) -> None:
        ...


class TelegramUserRepositoryProtocol(Protocol):
    def __init__(self, session: SessionProtocol) -> None:
        ...

    async def add(
        self,
        dm: TelegramUserEntity
    ) -> UUID:
        ...

    async def get(
        self,
        *,
        id: UUID | None = None,
        telegram_id: int | None = None,
        username: str | None = None,
        lock: Any | None = None,
    ) -> TelegramUserEntity | None:
        ...

    async def update(
        self,
        telegram_id: int,
        username: str | None,
        first_name: str | None,
        last_name: str | None,
    ) -> None:
        ...

    async def delete(self, telegram_id: int) -> None:
        ...


class HomeRepositoryProtocol(Protocol):
    async def create(self, home: HomeEntity) -> None: ...
    async def read(self, home_id: UUID) -> HomeEntity | None: ...
    async def update(self, home: HomeEntity) -> None: ...
    async def delete(self, home_id: UUID) -> None: ...


class HomeUserRoleRepositoryProtocol(Protocol):
    async def create(self, role: HomeUserRoleEntity) -> None: ...
    async def read(self, role_id: UUID) -> HomeUserRoleEntity | None: ...
    async def update(self, role: HomeUserRoleEntity) -> None: ...
    async def delete(self, role_id: UUID) -> None: ...


class SmartDeviceRepositoryProtocol(Protocol):
    async def create(self, device: SmartDeviceEntity) -> None: ...
    async def read(self, device_id: UUID) -> SmartDeviceEntity | None: ...
    async def update(self, device: SmartDeviceEntity) -> None: ...
    async def delete(self, device_id: UUID) -> None: ...


class UnitOfWorkProtocol(Protocol):
    users: TelegramUserRepositoryProtocol
    home: HomeRepositoryProtocol
    roles: HomeUserRoleRepositoryProtocol
    devices: SmartDeviceRepositoryProtocol

    async def __aenter__(self) -> Self:
        ...

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[types.TracebackType],
    ) -> None: 
        ...


