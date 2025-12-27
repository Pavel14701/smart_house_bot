from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID


@dataclass(frozen=True, slots=True)
class TelegramUserEntity:
    id: UUID
    telegram_id: int
    username: str | None
    first_name: str | None
    last_name: str | None


@dataclass(frozen=True, slots=True)
class AudioFileEntity:
    id: str
    content: bytes
    mimetype: str = "audio/wav"


@dataclass(frozen=True, slots=True)
class TextEventEntity:
    id: str
    text: str


class HomeRole(Enum):
    OWNER = "owner"
    ADMIN = "admin"
    GUEST = "guest"


@dataclass(frozen=True, slots=True)
class HomeEntity:
    id: UUID
    name: str
    address: str | None
    created_at: datetime


@dataclass(frozen=True, slots=True)
class HomeUserRoleEntity:
    id: UUID
    home_id: UUID
    user_id: UUID
    role: HomeRole
    created_at: datetime


@dataclass(frozen=True, slots=True)
class SmartDeviceEntity:
    id: UUID
    home_id: UUID
    name: str
    type: str
    location: str | None
    serial_number: str | None
    manufacturer: str | None
    model: str | None
    firmware_version: str | None
    is_active: bool
    registered_at: datetime
    last_seen: datetime | None
    custom_settings: dict[str, Any] | None
    ip_address: str | None
    mac_address: str | None
    battery_level: int | None
    connectivity: str | None
    status: str | None
    last_error: str | None
    updated_at: datetime
