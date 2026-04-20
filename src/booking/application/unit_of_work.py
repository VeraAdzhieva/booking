from __future__ import annotations

from types import TracebackType
from typing import Optional, Protocol, Type

from booking.domain.repository import ReservationRepository, TablesRepository


# Unit of Work Port (выходной порт)
class UnitOfWork(Protocol):
    reservations: Optional[ReservationRepository]
    tables: Optional[TablesRepository]

    def __enter__(self) -> "UnitOfWork":
        pass

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        pass

    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass
