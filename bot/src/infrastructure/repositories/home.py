import uuid  # noqa: F401
from typing import Any  # noqa: F401

from application.interfaces import HomeRepositoryProtocol
from domain.entities import HomeEntity  # noqa: F401
from domain.errors import (
    DomainError,  # noqa: F401
)
from sqlalchemy import text  # noqa: F401
from sqlalchemy.exc import IntegrityError, SQLAlchemyError  # noqa: F401
from sqlalchemy.ext.asyncio import AsyncSession


class HomeRepositorySQL(HomeRepositoryProtocol):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session