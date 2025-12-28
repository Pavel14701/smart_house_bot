import uuid
from typing import Literal

from application.interfaces import HomeUserRoleRepositoryProtocol
from domain.entities import HomeRole, HomeUserRoleEntity
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


class HomeUserRoleRepositorySQL(HomeUserRoleRepositoryProtocol):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, dm: HomeUserRoleEntity) -> uuid.UUID:
        stmt = text(
            """
            INSERT INTO home_user_roles (id, home_id, user_id, role, created_at)
            VALUES (:id, :home_id, :user_id, :role, :created_at)
            """
        )
        try:
            await self.session.execute(
                stmt,
                {
                    "id": dm.id,
                    "home_id": dm.home_id,
                    "user_id": dm.user_id,
                    "role": dm.role.value,
                    "created_at": dm.created_at,
                },
            )
            return dm.id
        except IntegrityError as e:
            raise EntityAlreadyExistsError("Role already exists") from e
        except SQLAlchemyError as e:
            raise DomainError("Database error while creating role") from e

    async def read(
        self,
        *,
        id: uuid.UUID,
        lock: Literal["update", "no_key_update", "share", "key_share"] | None = None,
    ) -> HomeUserRoleEntity | None:
        query = """
            SELECT * FROM home_user_roles 
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
            if row is None:
                return None
            return HomeUserRoleEntity(
                id=row["id"],
                home_id=row["home_id"],
                user_id=row["user_id"],
                role=HomeRole(row["role"]),
                created_at=row["created_at"],
            )
        except SQLAlchemyError as e:
            raise DomainError("Database error while reading role") from e

    async def update(self, id: uuid.UUID, new_role: HomeRole) -> None:
        stmt = text(
            """
            UPDATE home_user_roles
            SET role = :role
            WHERE id = :id
            """
        )
        try:
            result = await self.session.execute(
                stmt, {"id": id, "role": new_role.value}
            )
            if getattr(result, "rowcount", 0) == 0:
                raise EntityNotFoundError("Role not found for update")
        except EntityNotFoundError:
            raise
        except SQLAlchemyError as e:
            raise EntityUpdateError("Error updating role") from e

    async def delete(self, id: uuid.UUID) -> None:
        stmt = text("""
            DELETE FROM home_user_roles 
            WHERE id = :id
        """)
        try:
            result = await self.session.execute(stmt, {"id": id})
            if getattr(result, "rowcount", 0) == 0:
                raise EntityNotFoundError("Role not found for delete")
        except EntityNotFoundError:
            raise
        except SQLAlchemyError as e:
            raise EntityDeleteError("Error deleting role") from e