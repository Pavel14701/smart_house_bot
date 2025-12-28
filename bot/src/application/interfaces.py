import types
from typing import Any, Optional, Protocol, Self, Type  # type: ignore [attr-defined]
from uuid import UUID

from domain.entities import (
    AudioFileEntity,
    HomeEntity,
    HomeRole,
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

    async def create(
        self,
        dm: TelegramUserEntity
    ) -> UUID:
        ...

    async def read(
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
    def __init__(self, session: SessionProtocol) -> None:
        ...

    async def create(self, dm: HomeEntity) -> UUID: 
        ...

    async def read(self, *, id: UUID, lock: Any) -> HomeEntity | None: 
        ...
    
    async def update(
        self, 
        id: UUID, 
        name: str | None, 
        address: str | None
    ) -> None: 
        ...
    
    async def delete(self, id: UUID) -> None: 
        ...


class HomeUserRoleRepositoryProtocol(Protocol):
    def __init__(self, session: SessionProtocol) -> None:
        ...

    async def create(self, dm: HomeUserRoleEntity) -> UUID: 
        ...
    
    async def read(self, *, id: UUID, lock: Any) -> HomeUserRoleEntity | None: 
        ...
    
    async def update(self, id: UUID, new_role: HomeRole) -> None: 
        ...
    
    async def delete(self, id: UUID) -> None: 
        ...


class SmartDeviceRepositoryProtocol(Protocol):
    def __init__(self, session: SessionProtocol) -> None:
        ...

    async def create(self, dm: SmartDeviceEntity) -> UUID: 
        ...
    
    async def read(
        self,
        *,
        id: UUID | None = None,
        serial_number: str | None = None,
        mac_address: str | None = None,
        home_id: UUID | None = None,
        name: str | None = None,
        lock: Any,
    ) -> SmartDeviceEntity | None:        
        ...
    
    async def update(self, dm: SmartDeviceEntity) -> None: 
        ...
    
    async def delete(self, id: UUID) -> None: 
        ...


class UnitOfWorkProtocol(Protocol):
    session: SessionProtocol
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


