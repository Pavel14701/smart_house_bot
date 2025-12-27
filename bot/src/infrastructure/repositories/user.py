import uuid
from typing import Any, Literal

from application.interfaces import TelegramUserRepositoryProtocol
from domain.entities import TelegramUserEntity
from domain.errors import (
    DomainError,
    UserAlreadyExistsError,
    UserDeleteError,
    UserNotFoundError,
    UserUpdateError,
)
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


class TelegramUserRepositorySQL(TelegramUserRepositoryProtocol):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(
        self,
        dm: TelegramUserEntity
    ) -> uuid.UUID:
        stmt = text(
            """
            INSERT INTO telegram_users (
                id,
                telegram_id,
                username,
                first_name,
                last_name
            )
            VALUES (
                :id,
                :telegram_id,
                :username,
                :first_name,
                :last_name
            )
            """
        )
        try:
            await self.session.execute(
                stmt,
                {
                    "id": dm.id,
                    "telegram_id": dm.telegram_id,
                    "username": dm.username,
                    "first_name": dm.first_name,
                    "last_name": dm.last_name,
                },
            )
            return dm.id
        except IntegrityError as e:
            raise UserAlreadyExistsError(
                "A user with this telegram_id already exists."
            ) from e
        except SQLAlchemyError as e:
            raise DomainError("Database error while adding user") from e

    async def get(
        self,
        *,
        id: uuid.UUID | None = None,
        telegram_id: int | None = None,
        username: str | None = None,
        lock: Literal["update", "no_key_update", "share", "key_share"] | None = None,
    ) -> TelegramUserEntity | None:
        params: dict[str, Any] = {}
        if id is not None:
            query = """
                SELECT * FROM telegram_users 
                WHERE id = :id
            """
            params["id"] = id
        elif telegram_id is not None:
            query = """
                SELECT * FROM telegram_users 
                WHERE telegram_id = :telegram_id
            """
            params["telegram_id"] = telegram_id
        elif username is not None:
            query = """
                SELECT * FROM telegram_users 
                WHERE username = :username
            """
            params["username"] = username
        else:
            raise ValueError("Нужно указать хотя бы один уникальный ключ")
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
            if row is None:
                return None
            return TelegramUserEntity(**row)
        except SQLAlchemyError as e:
            raise DomainError("Database error while reading user") from e

    async def update(
        self,
        telegram_id: int,
        username: str | None,
        first_name: str | None,
        last_name: str | None,
    ) -> None:
        stmt = text(
            """
            UPDATE telegram_users
            SET username = :username,
                first_name = :first_name,
                last_name = :last_name
            WHERE telegram_id = :telegram_id
            """
        )
        try:
            result = await self.session.execute(
                stmt,
                {
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name,
                    "telegram_id": telegram_id,
                },
            )
            if getattr(result, "rowcount", 0) == 0:
                raise UserNotFoundError("User not found for update")
        except UserNotFoundError:
            raise
        except SQLAlchemyError as e:
            raise UserUpdateError("Error updating user") from e

    async def delete(self, telegram_id: int) -> None:
        stmt = text(
            """
            DELETE FROM telegram_users
            WHERE telegram_id = :telegram_id
            """
        )
        try:
            result = await self.session.execute(stmt, {"telegram_id": telegram_id})
            if getattr(result, "rowcount", 0) == 0:
                raise UserNotFoundError("User to delete not found")
        except UserNotFoundError:
            raise
        except SQLAlchemyError as e:
            raise UserDeleteError("Error deleting user") from e
