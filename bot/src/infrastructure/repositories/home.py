import uuid
from typing import Literal

from application.interfaces import HomeRepositoryProtocol
from domain.entities import HomeEntity
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


class HomeRepositorySQL(HomeRepositoryProtocol):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, dm: HomeEntity) -> uuid.UUID:
        stmt = text(
            """
            INSERT INTO homes (id, name, address, created_at)
            VALUES (:id, :name, :address, :created_at)
            """
        )
        try:
            await self.session.execute(
                stmt,
                {
                    "id": dm.id,
                    "name": dm.name,
                    "address": dm.address,
                    "created_at": dm.created_at,
                },
            )
            return dm.id
        except IntegrityError as e:
            raise EntityAlreadyExistsError("Home already exists") from e
        except SQLAlchemyError as e:
            raise DomainError("Database error while creating home") from e

    async def read(
        self,
        *,
        id: uuid.UUID,
        lock: Literal["update", "no_key_update", "share", "key_share"] | None = None,
    ) -> HomeEntity | None:
        query = """
            SELECT * FROM homes 
            WHERE id = :id
        """
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
            result = await self.session.execute(text(query), {"id": id})
            row = result.mappings().first()
            return None if row is None else HomeEntity(**row)
        except SQLAlchemyError as e:
            raise DomainError("Database error while reading home") from e

    async def update(
        self, 
        id: uuid.UUID, 
        name: str | None, 
        address: str | None
    ) -> None:
        stmt = text(
            """
            UPDATE homes
            SET name = :name,
                address = :address
            WHERE id = :id
            """
        )
        try:
            result = await self.session.execute(
                stmt, {"id": id, "name": name, "address": address}
            )
            if getattr(result, "rowcount", 0) == 0:
                raise EntityNotFoundError("Home not found for update")
        except EntityNotFoundError:
            raise
        except SQLAlchemyError as e:
            raise EntityUpdateError("Error updating home") from e

    async def delete(self, id: uuid.UUID) -> None:
        stmt = text("DELETE FROM homes WHERE id = :id")
        try:
            result = await self.session.execute(stmt, {"id": id})
            if getattr(result, "rowcount", 0) == 0:
                raise EntityNotFoundError("Home not found for delete")
        except EntityNotFoundError:
            raise
        except SQLAlchemyError as e:
            raise EntityDeleteError("Error deleting home") from e
