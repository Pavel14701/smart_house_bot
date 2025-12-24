from typing import Protocol

from sqlalchemy import UUID


class UUIDGenerator(Protocol):
    def __call__(self) -> UUID:
        ...
