from types import TracebackType
from typing import Callable, Self, Type  # type: ignore [attr-defined]

from application.interfaces import (
    HomeRepositoryProtocol,
    HomeUserRoleRepositoryProtocol,
    SessionProtocol,
    SmartDeviceRepositoryProtocol,
    TelegramUserRepositoryProtocol,
)


class UnitOfWork:
    """
    Unit of Work pattern for managing an asynchronous transaction and repository
    instances within a single context.

    This class encapsulates the lifecycle of a transaction: it begins when entering
    the context, commits changes if no exception occurs, and rolls back if an
    exception is raised. All repositories share the same session, ensuring
    consistency across operations.

    Parameters
    ----------
    session : SessionProtocol
        An asynchronous session implementing `begin`, `commit`, and `rollback`.
    users : type[TelegramUserRepositoryProtocol]
        Repository class for working with Telegram users.
    home : type[HomeRepositoryProtocol]
        Repository class for managing homes.
    roles : type[HomeUserRoleRepositoryProtocol]
        Repository class for managing user roles within a home.
    devices : type[SmartDeviceRepositoryProtocol]
        Repository class for managing smart devices.

    Notes
    -----
    The repository parameters are class types that satisfy the corresponding
    protocols, not protocol instances themselves. This allows passing different
    concrete implementations (e.g., SQL-based or in-memory fakes) while keeping
    the UnitOfWork generic.
    """

    def __init__(
        self,
        session: SessionProtocol,
        users: Callable[[SessionProtocol], TelegramUserRepositoryProtocol],
        home: Callable[[SessionProtocol], HomeRepositoryProtocol],
        roles: Callable[[SessionProtocol], HomeUserRoleRepositoryProtocol],
        devices: Callable[[SessionProtocol], SmartDeviceRepositoryProtocol],
    ) -> None:
        """
        Initialize the UnitOfWork.

        Stores the session and instantiates repository objects using the provided
        repository classes. Each repository is expected to accept the session in
        its constructor.
        """
        self._session = session
        self._users = users(session)
        self.home = home(session)
        self.roles = roles(session)
        self.devices = devices(session)

    async def __aenter__(self) -> Self:  # type: ignore [attr-defined]
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
        exc_type : Type[BaseException] | None
            The exception type if an exception was raised, otherwise None.
        exc : BaseException | None
            The exception instance if an exception was raised, otherwise None.
        tb : TracebackType | None
            The traceback object if an exception was raised, otherwise None.

        Notes
        -----
        Implementations may extend this method to add logging, error translation
        (e.g., infrastructure exceptions → domain exceptions), or additional
        cleanup steps. If commit fails, callers should ensure rollback is performed
        to avoid leaving the session in an inconsistent state.
        """
        if exc_type:
            await self._session.rollback()
        else:
            await self._session.commit()
