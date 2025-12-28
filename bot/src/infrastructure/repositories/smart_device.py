import uuid
from dataclasses import asdict
from typing import Any, Literal

from application.interfaces import SmartDeviceRepositoryProtocol
from domain.entities import SmartDeviceEntity
from domain.errors import (
    DomainError,
    EntityAlreadyExistsError,
    EntityDeleteError,
    EntityNotFoundError,
    EntityUpdateError,
)
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


class SmartDeviceRepositorySQL(SmartDeviceRepositoryProtocol):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, dm: SmartDeviceEntity) -> uuid.UUID:
        stmt = text(
            """
            INSERT INTO smart_devices (
                id, home_id, name, type, location, serial_number,
                manufacturer, model, firmware_version, is_active,
                registered_at, last_seen, custom_settings,
                ip_address, mac_address, battery_level,
                connectivity, status, last_error, updated_at
            )
            VALUES (
                :id, :home_id, :name, :type, :location, :serial_number,
                :manufacturer, :model, :firmware_version, :is_active,
                :registered_at, :last_seen, :custom_settings,
                :ip_address, :mac_address, :battery_level,
                :connectivity, :status, :last_error, :updated_at
            )
            """
        )
        try:
            await self.session.execute(stmt, asdict(dm))
            return dm.id
        except IntegrityError as e:
            raise EntityAlreadyExistsError("SmartDevice already exists") from e
        except SQLAlchemyError as e:
            raise DomainError("Database error while creating SmartDevice") from e

    async def read(
        self,
        *,
        id: uuid.UUID | None = None,
        serial_number: str | None = None,
        mac_address: str | None = None,
        home_id: uuid.UUID | None = None,
        name: str | None = None,
        lock: Literal["update", "no_key_update", "share", "key_share"] | None = None,
    ) -> SmartDeviceEntity | None:
        query = "SELECT * FROM smart_devices WHERE "
        params: dict[str, Any] = {}
        if id is not None:
            query += "id = :id"
            params["id"] = id
        elif serial_number is not None:
            query += "serial_number = :serial_number"
            params["serial_number"] = serial_number
        elif mac_address is not None:
            query += "mac_address = :mac_address"
            params["mac_address"] = mac_address
        elif home_id is not None and name is not None:
            query += "home_id = :home_id AND name = :name"
            params["home_id"] = home_id
            params["name"] = name
        else:
            raise ValueError("Must specify at least one unique key")
        if lock is not None:
            if lock == "update":
                query += " FOR UPDATE"
            elif lock == "no_key_update":
                query += " FOR NO KEY UPDATE"
            elif lock == "share":
                query += " FOR SHARE"
            elif lock == "key_share":
                query += " FOR KEY SHARE"
        try:
            result = await self.session.execute(text(query), params)
            row = result.mappings().first()
            return None if row is None else SmartDeviceEntity(**row)
        except SQLAlchemyError as e:
            raise DomainError("Database error while reading SmartDevice") from e

    async def update(self, dm: SmartDeviceEntity) -> None:
        stmt = text(
            """
            UPDATE smart_devices
            SET home_id = :home_id,
                name = :name,
                type = :type,
                location = :location,
                serial_number = :serial_number,
                manufacturer = :manufacturer,
                model = :model,
                firmware_version = :firmware_version,
                is_active = :is_active,
                registered_at = :registered_at,
                last_seen = :last_seen,
                custom_settings = :custom_settings,
                ip_address = :ip_address,
                mac_address = :mac_address,
                battery_level = :battery_level,
                connectivity = :connectivity,
                status = :status,
                last_error = :last_error,
                updated_at = :updated_at
            WHERE id = :id
            """
        )
        try:
            result = await self.session.execute(stmt, asdict(dm))
            if getattr(result, "rowcount", 0) == 0:
                raise EntityNotFoundError("SmartDevice not found for update")
        except EntityNotFoundError:
            raise
        except SQLAlchemyError as e:
            raise EntityUpdateError("Error updating SmartDevice") from e

    async def delete(self, id: uuid.UUID) -> None:
        stmt = text("""
            DELETE FROM smart_devices 
            WHERE id = :id
        """)
        try:
            result = await self.session.execute(stmt, {"id": id})
            if getattr(result, "rowcount", 0) == 0:
                raise EntityNotFoundError("SmartDevice not found for delete")
        except EntityNotFoundError:
            raise
        except SQLAlchemyError as e:
            raise EntityDeleteError("Error deleting SmartDevice") from e
