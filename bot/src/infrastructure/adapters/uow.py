from types import TracebackType
from typing import Self, Type  # type: ignore [attr-defined]

from application.interfaces import (
    HomeRepositoryProtocol,
    HomeUserRoleRepositoryProtocol,
    SessionProtocol,
    SmartDeviceRepositoryProtocol,
    TelegramUserRepositoryProtocol,
)


class UnitOfWork:
    """
    Unit of Work that manages a session and a repository instance for the
    duration of an asynchronous transactional context.

    The UnitOfWork starts a transaction on enter and commits or rolls back
    on exit depending on whether an exception occurred.

    Parameters
    ----------
    session:
        An object implementing SessionProtocol (must provide async begin,
        commit and rollback methods).
    users:
        A repository class (not an instance) that implements
        TelegramUserRepositoryProtocol. The repository will be instantiated
        with the provided session.
    """

    def __init__(
        self, 
        session: SessionProtocol, 
        users: type[TelegramUserRepositoryProtocol],
        home: type[HomeRepositoryProtocol],
        roles: type[HomeUserRoleRepositoryProtocol],
        devices: type[SmartDeviceRepositoryProtocol],
    ) -> None:
        """
        Initialize UnitOfWork.

        This stores the session and creates a repository instance using the
        provided repository class. The repository is expected to accept the
        session in its constructor.

        Notes
        -----
        The repository parameter is a class type that satisfies the protocol,
        not the protocol itself. This allows passing different concrete
        implementations (e.g. SQL or in-memory fake) while keeping the unit
        of work generic.
        """
        self._session = session
        self._users = users(session)

    async def __aenter__(self) -> Self:
        """
        Enter the asynchronous context and begin a transaction.

        Returns
        -------
        Self
            The UnitOfWork instance with an active transaction.
        """
        await self._session.begin()
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """
        Exit the asynchronous context.

        If an exception occurred inside the context, roll back the transaction.
        Otherwise, commit the transaction.

        Parameters
        ----------
        exc_type:
            The exception type if an exception was raised, otherwise None.
        exc:
            The exception instance if an exception was raised, otherwise None.
        tb:
            The traceback object if an exception was raised, otherwise None.

        Notes
        -----
        Implementations may extend this method to add logging, error
        translation (infrastructure exceptions -> domain exceptions), or
        additional cleanup steps. If commit fails, callers should ensure the
        transaction is rolled back to avoid leaving the session in an
        inconsistent state.
        """
        if exc_type:
            await self._session.rollback()
        else:
            await self._session.commit()
